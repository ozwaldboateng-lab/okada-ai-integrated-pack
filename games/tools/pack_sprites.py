#!/usr/bin/env python3
"""単一ファイル HTML ゲームに埋め込まれた画像を、見た目を保ったまま軽くする。

fantasianproto.html は 1 枚の HTML にすべての絵を base64 のデータURIで
抱えている。配布が 1 ファイルで済む代わりに、ファイルの 9 割以上が画像で
占められ、初回読み込みが重い。

このツールは各データURIを取り出して WebP に詰め直し、元の場所へ書き戻す。
1 枚ごとに非可逆と可逆の両方を試し、非可逆が可逆より十分小さくなる絵だけ
非可逆を採る。平坦な絵は可逆でも小さくなるので、そこで画質を捨てる理由がない。

  python3 games/tools/pack_sprites.py --report            # 何がどれだけ減るか見る
  python3 games/tools/pack_sprites.py --apply             # 書き換える（控えを残す）
  python3 games/tools/pack_sprites.py --apply --dry-run   # 書き換えずに結果だけ
  python3 games/tools/pack_sprites.py --restore           # 控えから戻す

WebP を選んだ理由:
  減色（PNG-8）はこの絵には効かない。手描き調のグラデーションが主体で、
  色数を 256 まで落としても PNG は 5% ほどしか縮まなかった。一方 WebP は
  同じ絵を 3〜6 分の 1 にする。透明度は libwebp が既定で可逆に持つため、
  非可逆の品質を下げても輪郭に滲みが出ない（pack() で毎回確かめている）。

誤差の数値を自動判定に使わない理由は LOSSY_WORTH_IT の下のコメントに書いた。
画質の可否は最終的に目で決めるものなので、--report の数値は判断材料として
出すに留め、既定では誰も弾かない。
"""

import argparse
import base64
import io
import re
import shutil
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError:
    sys.exit('Pillow と numpy が要ります:  pip install Pillow numpy')


HTML = Path(__file__).resolve().parents[1] / 'fantasianproto.html'
BACKUP_SUFFIX = '.pre-webp.bak'

# データURIと、その直前に書かれた識別子（sprite名）をまとめて拾う
URI_RE = re.compile(r'data:image/(png|jpeg|jpg|webp);base64,([A-Za-z0-9+/=]+)')
KEY_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*[:=]\s*['\"`]?\s*$")
KEY_FALLBACK_RE = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*[:=]")

# 既定の品質。実表示サイズ（雑魚 58px・古竜 252px）で元と並べて目視したところ、
# q=85 でも見分けがつかなかった。少し余裕を取って 90 を既定にしている。
DEFAULT_QUALITY = 90

# 非可逆が可逆に対してこの割合より小さくならないなら、可逆を選ぶ。
# わずかしか縮まないのに画質を捨てるのは損なので。
LOSSY_WORTH_IT = 0.85

# 誤差は「門番」ではなく「報告」として出す。
# WebP の非可逆は常にクロマを 4:2:0 に間引くため、彩度の細かい絵（大蛇・悪魔など）は
# 品質をいくら上げても誤差が 8〜10 あたりで頭打ちになる。この底は数値には出るが、
# 実際に描かれる大きさでは見えない。したがって数値で自動的に弾くと、
# 見えない差のために一番効く絵ほど可逆へ落ちてしまい、目的を取り違える。
# --max-error を渡したときだけ、明らかな破綻を捕まえる網として働かせる。


class Asset:
    """HTML 中の 1 枚。位置と中身と、詰め直した結果を持つ。"""

    def __init__(self, name, fmt, b64, start, end):
        self.name = name
        self.fmt = fmt
        self.b64 = b64
        self.start = start          # data: の 'd' の位置
        self.end = end              # base64 本体の終端
        self.raw = base64.b64decode(b64)
        self.image = Image.open(io.BytesIO(self.raw))
        self.image.load()
        self.has_alpha = self.image.mode in ('RGBA', 'LA') or 'transparency' in self.image.info
        self.image = self.image.convert('RGBA' if self.has_alpha else 'RGB')
        self.packed = None          # bytes
        self.quality = None
        self.error = None           # (mean, p999)
        self.resized_to = None      # --max-size で縮めた場合の寸法
        self.skip_reason = 'そのまま'  # 触らなかった理由

    @property
    def old_bytes(self):
        return len(self.raw)

    @property
    def new_bytes(self):
        return len(self.packed) if self.packed else len(self.raw)

    @property
    def size(self):
        return self.image.size


def find_assets(html):
    """HTML からデータURIを順に拾う。名前が重複したら連番で区別する。"""
    assets, seen = [], {}
    for m in URI_RE.finditer(html):
        before = html[max(0, m.start() - 240):m.start()]
        key = KEY_RE.findall(before) or KEY_FALLBACK_RE.findall(before)
        name = key[-1] if key else 'image'
        seen[name] = seen.get(name, 0) + 1
        if seen[name] > 1:
            name = f'{name}#{seen[name]}'
        assets.append(Asset(name, m.group(1), m.group(2), m.start(), m.end()))
    return assets


def composite(im, bg=110):
    """透明度を持つ絵を中間色の地に重ねて、実際に目に入る画素値にする。

    透明な画素の RGB は WebP が自由に書き換えてよい領域なので、そのまま
    比べると「見えない部分の差」で誤差が跳ね上がり、判定にならない。
    """
    arr = np.asarray(im, dtype=np.float32)
    if arr.shape[2] == 3:
        return arr
    rgb, a = arr[:, :, :3], arr[:, :, 3:4] / 255.0
    return rgb * a + bg * (1.0 - a)


def measure(original, decoded):
    """composite 後の差を、平均と上位 0.1% の二軸で返す。"""
    d = np.abs(composite(original) - composite(decoded))
    per_pixel = d.max(axis=2)
    return float(per_pixel.mean()), float(np.percentile(per_pixel, 99.9))


def encode(im, quality, lossless=False):
    bio = io.BytesIO()
    im.save(bio, 'WEBP', quality=quality, method=6, lossless=lossless)
    return bio.getvalue()


def alpha_is_intact(original, decoded):
    """透明度が 1 階調でも動いていないかを確かめる。輪郭の滲みはここに出る。"""
    if original.mode != 'RGBA':
        return True
    a = np.asarray(original.getchannel('A'), dtype=np.int16)
    b = np.asarray(decoded.getchannel('A'), dtype=np.int16)
    return int(np.abs(a - b).max()) == 0


def _decode(data, mode):
    im = Image.open(io.BytesIO(data))
    im.load()
    return im.convert(mode)


def pack(asset, quality, max_error=None, max_size=None, force=False):
    """1 枚を詰め直す。非可逆と可逆を両方試し、割に合うほうを採る。

    - すでに WebP の絵は触らない。再圧縮は世代劣化を重ねるだけで、
      二度目以降はほとんど縮まない（実測で 1.5%）。--force で上書きできる
    - 非可逆が可逆の LOSSY_WORTH_IT 未満にならないなら可逆を選ぶ
    - max_error を渡した場合、それを超えた非可逆は捨てて可逆へ退く
    - どちらも元より大きければ、その絵は触らない
    """
    if asset.fmt == 'webp' and not force and not max_size:
        asset.skip_reason = '変換済み'
        return False

    im = asset.image
    if max_size and max(im.size) > max_size:
        ratio = max_size / max(im.size)
        im = im.resize((round(im.width * ratio), round(im.height * ratio)), Image.LANCZOS)
        asset.resized_to = im.size

    lossless = encode(im, 100, lossless=True)
    lossy = encode(im, quality)
    err = measure(im, _decode(lossy, im.mode))

    use_lossy = len(lossy) < len(lossless) * LOSSY_WORTH_IT
    if use_lossy and not alpha_is_intact(im, _decode(lossy, im.mode)):
        use_lossy = False       # 輪郭に滲みが出るなら、軽さより形を採る
    if use_lossy and max_error is not None and err[0] > max_error:
        use_lossy = False

    if use_lossy:
        data, q = lossy, quality
    else:
        data, q, err = lossless, 'lossless', (0.0, 0.0)

    if len(data) >= asset.old_bytes and not max_size:
        return False            # 詰め直しても得しない絵
    asset.packed, asset.quality, asset.error = data, q, err
    return True


def rewrite(html, assets):
    """後ろから差し替える。前から書き換えると以降の位置がずれる。"""
    out = html
    for a in sorted(assets, key=lambda x: x.start, reverse=True):
        if not a.packed:
            continue
        uri = 'data:image/webp;base64,' + base64.b64encode(a.packed).decode('ascii')
        out = out[:a.start] + uri + out[a.end:]
    return out


def human(n):
    return f'{n / 1024:.1f}K' if n < 1024 * 1024 else f'{n / 1024 / 1024:.2f}M'


def report(assets, html_len, applied):
    packed = [a for a in assets if a.packed]
    old = sum(a.old_bytes for a in assets)
    new = sum(a.new_bytes for a in assets)
    other = html_len - int(old * 4 / 3)

    width = max((len(a.name) for a in assets), default=8)
    print(f"{'画像':<{width}} {'寸法':>11} {'現状':>9} {'WebP':>9} {'倍率':>7} {'方式':>9} "
          f"{'誤差(平均/上位0.1%)':>20}")
    for a in sorted(assets, key=lambda x: x.old_bytes - x.new_bytes, reverse=True):
        w, h = a.resized_to or a.size
        if a.packed:
            ratio = f'{a.old_bytes / a.new_bytes:.1f}x'
            err = '—' if a.quality == 'lossless' else f'{a.error[0]:.2f} / {a.error[1]:.1f}'
            q = '可逆' if a.quality == 'lossless' else f'q{a.quality}'
        else:
            ratio, err, q = '—', '—', a.skip_reason
        print(f'{a.name:<{width}} {w:>5}x{h:<5} {human(a.old_bytes):>9} '
              f'{human(a.new_bytes):>9} {ratio:>7} {q:>9} {err:>20}')

    print()
    print(f'  詰め直した絵     {len(packed)} / {len(assets)} 枚')
    print(f'  画像の実バイト   {human(old)} → {human(new)}   ({old / max(new, 1):.1f} 分の 1)')
    print(f'  base64 にすると  {human(int(old * 4 / 3))} → {human(int(new * 4 / 3))}')
    print(f'  HTML 本体（画像以外） {human(other)}')
    verb = 'なった' if applied else 'なる見込み'
    print(f'  ファイル全体     {human(html_len)} → {human(other + int(new * 4 / 3))}   {verb}')


def main():
    ap = argparse.ArgumentParser(description='埋め込み画像を WebP に詰め直す')
    ap.add_argument('--file', type=Path, default=HTML, help='対象の HTML')
    ap.add_argument('--report', action='store_true', help='調べるだけで書き換えない')
    ap.add_argument('--apply', action='store_true', help='HTML を書き換える')
    ap.add_argument('--dry-run', action='store_true', help='--apply の計算だけして書かない')
    ap.add_argument('--restore', action='store_true', help='控えから元に戻す')
    ap.add_argument('--quality', type=int, default=DEFAULT_QUALITY,
                    help=f'WebP の品質（既定 {DEFAULT_QUALITY}）')
    ap.add_argument('--max-error', type=float, default=None,
                    help='平均誤差がこれを超えたら可逆に退く（既定は無効）')
    ap.add_argument('--max-size', type=int, default=None,
                    help='長辺がこれを超える絵は縮めてから詰める（既定は縮めない）')
    ap.add_argument('--force', action='store_true',
                    help='すでに WebP の絵も詰め直す（世代劣化するので通常は不要）')
    ap.add_argument('--only', action='append', default=None,
                    help='この名前の絵だけ扱う（繰り返し指定可）')
    args = ap.parse_args()

    path = args.file
    backup = path.with_suffix(path.suffix + BACKUP_SUFFIX)

    if args.restore:
        if not backup.exists():
            sys.exit(f'控えがありません: {backup}')
        shutil.copy2(backup, path)
        print(f'戻しました: {backup.name} → {path.name}')
        return

    if not (args.report or args.apply):
        args.report = True

    html = path.read_text(encoding='utf-8')
    assets = find_assets(html)
    if args.only:
        assets = [a for a in assets if a.name in args.only]
    if not assets:
        sys.exit('データURIが見つかりませんでした。')

    print(f'{path} … 画像 {len(assets)} 枚を調べています（品質 {args.quality}）')
    for a in assets:
        pack(a, args.quality, args.max_error, args.max_size, args.force)

    applied = False
    if args.apply and not args.dry_run:
        if not backup.exists():
            shutil.copy2(path, backup)
            print(f'控えを作りました: {backup.name}')
        out = rewrite(html, assets)
        path.write_text(out, encoding='utf-8')
        html_len_after = len(out.encode())
        applied = True
        report(assets, len(html.encode()), applied)
        print(f'  実測             {human(html_len_after)}')
        return

    report(assets, len(html.encode()), applied)


if __name__ == '__main__':
    main()
