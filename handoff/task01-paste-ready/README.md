# Okada AI v1.7 Task-01 Paste-Ready Pack

このパックは、Codex と Claude Code の両方に **task-01: kernel contract hardening** を
そのまま貼って投げられる最短文面をまとめたものです。

## 目的
- 同じ仕様に基づいて、Codex / Claude Code がそれぞれスタンドアローンで task-01 を実装する
- 比較は厳密採点ではなく、成果物と作業感の目視比較で行う

## 使い方
1. `docs/01_task01_brief.md` を先に読む
2. 実行相手に応じて次のどちらかをそのまま貼る
   - Codex: `prompts/01_codex_task01_paste_ready.md`
   - Claude Code: `prompts/02_claude_task01_paste_ready.md`
3. 両者の結果を `notes/01_quick_comparison_template.md` にメモする

## 前提
- source of truth は `registry/*.yaml`, `api/*.yaml`, `schemas/*.json`, `docs/*.md`
- 今回は task-01 のみを対象とする
- 実装は repo 内で完結する範囲に限定する
