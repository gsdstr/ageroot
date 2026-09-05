# Extraction manifest and adapter seams

Checkout verified HEAD: `9424c58e1cfc17a709d1adfa13678e876edfe409`.
Checkout root: `/var/folders/qb/bj_m6p_j4kjc76cpt6nsz3fw0000gn/T/ageroot-memory-upstream-lq66ra8z`.
External AGENTS not followed. Inspected Python through AST imports and targeted source reads; no code executed.

## Concrete file closure

Below is proposed closure for all nine upstream memory modules, workflow command surface including show, and context/budget entry points. Paths relative to upstream .agent/. Includes 27 Python files. Optional skill-loader handling noted separately.

- `harness/context_budget.py` — SHA256 `2cce4f8ea293e68910e4bb87004c0401eaf58c44f0b33bce12088f7fe3c00670`
- `harness/hooks/__init__.py` — SHA256 `e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855`
- `harness/hooks/_episodic_io.py` — SHA256 `471456754c8a1e9b9750501cba677e642d3f7ccc5e7d99a105ab6958ca911cc9`
- `harness/hooks/_provenance.py` — SHA256 `93fab6e3de70ecbbe4aa036436e95af2747750c185f33344b3de54ba758b3767`
- `harness/hooks/on_failure.py` — SHA256 `1556da1a21a205f6196473749f222d698ceb7546aa482fc98229f56ba90d49a8`
- `harness/hooks/post_execution.py` — SHA256 `5fda65dc276ca0f0f22c34964df56c3a2f739fc5d60b8d23f54ced5218e83cb3`
- `harness/salience.py` — SHA256 `8272b133cf4a7282e7393fe929423534359739dd90154a686e729eb832f86199`
- `harness/text.py` — SHA256 `22fe0b84aacb4796b930fcb3f4a351d7bb96c9c145427ebf084254c9cfb6e081`
- `memory/archive.py` — SHA256 `279eb97507acd1be0dc9d44836d4b27ff84a342c758161b2ef6393c1d5cbead2`
- `memory/auto_dream.py` — SHA256 `a28641de169677416d36698956b9fe03f1825eed7d4d9a34594982ae42519bd9`
- `memory/cluster.py` — SHA256 `6b0445900ade2fc180a389cbcc23fb53a64de48ef82bbd8e5c26908f744e49e7`
- `memory/decay.py` — SHA256 `9b46a6b0661a3fa9cccf8ec12b59552e4f307676932202b01bc8fbd9755da28d`
- `memory/memory_search.py` — SHA256 `2d5a095ef733d9fe4f60cd306729d6bf17b4469f92ee79dd4f37609dcc397ee0`
- `memory/promote.py` — SHA256 `f218de0cc294e74870499a0bf218e6476b4cf339871f46f3691c26229192cd71`
- `memory/render_lessons.py` — SHA256 `b53aa21366db1ba6eb50eb1549c0821906499ae3ed55bb62ca2c3c69db5bee94`
- `memory/review_state.py` — SHA256 `cc02d6b9c9cb8b262431c8bce8ffeda5a493b784ac9c53624092238badeb31df`
- `memory/validate.py` — SHA256 `4eba979f9839a5a5f1d559a414c4520d9eaf027f0b8b42dbf63d48fe53e050db`
- `tools/budget_tracker.py` — SHA256 `99de693ae613bed86073f6d1a653400ac11426a82ec673043e69a62cfad814c2`
- `tools/graduate.py` — SHA256 `5371f15efb158eb4e53b3310758a080d359cff54d155046eb6c3491d575d09af`
- `tools/learn.py` — SHA256 `68adf2ec4774fc669f7b2b9d624b4efe91f61667d70c658fb9e4a30fa6663892`
- `tools/list_candidates.py` — SHA256 `215449bbea59f615f0df56fd996cc84b166ad08ef3f0f7fc4855ed2bcc43e881`
- `tools/memory_reflect.py` — SHA256 `6f9fb4e1e957ed2f15bf3c31add98c078b6df9f49503465c8c998687a60c1dde`
- `tools/recall.py` — SHA256 `486674ba66bf2a9ff16c3451fd4a2948dacb0ce05bd9f250f26951610b3f3564`
- `tools/reject.py` — SHA256 `8f86d95f6b3e2ca4190ffdba19e721f7dc742c0cf5dc3dac48f8b48bdb3b610c`
- `tools/reopen.py` — SHA256 `5ab15f022ef83a59e96689b65f112dff8b6900b6a18a22a05a95e7049becfeef`
- `tools/retract_lesson.py` — SHA256 `6d14198c5e3817a880a4c255e8313145042f28b4877048ab0b2c96a0063f32b8`
- `tools/show.py` — SHA256 `8df8ced299257ff033e7c291fa4884b5351cf9ab532b3827feba5ae5b41f8af0`

Also retain top-level upstream LICENSE and applicable attribution. Do not copy upstream memory data, AGENTS preferences/instructions or candidates fixtures as runtime assets.

### Internal edges

- memory_reflect -> hooks.post_execution/on_failure -> hooks._provenance/_episodic_io.
- recall -> text.word_set, render_lessons.superseded_by_map; optional log_recall -> memory_reflect.reflect.
- learn -> text.word_set, cluster.pattern_id; CLI subprocess graduate.py.
- graduate -> review_state.mark_graduated, validate.heuristic_check, render_lessons append/load/render.
- reject/reopen/list_candidates -> review_state.
- retract_lesson -> render_lessons append/load/render.
- auto_dream -> promote/validate/review_state/decay/archive; promote -> cluster/review_state/validate; cluster -> text/salience; validate -> text; decay -> salience.
- budget_tracker -> context_budget -> text/salience plus OPTIONAL lazy skill_loader.progressive_load. Exception handled as empty skill list. For literal full context behavior include tools/skill_loader.py (stdlib only), but it reads upstream skills manifest and preconditions, outside memory-only scope. Minimal documented adaptation: remove/disable matched-skill block lines 168-180, letting consumer harness load its skills. No conductor/llm/provider needed.
- show uses stdlib only, but reads skills/_manifest.jsonl and ../VERSION for dashboard beyond memory. Redirect to runtime manifest/version or omit unrelated sections.
- All non-internal Python imports in this closure stdlib; fcntl optional POSIX. Git subprocess for provenance, rg/grep optional search fallback. No model SDK or embedding provider.

## Workflow append-only: correction and findings

**Retraction already append-only upstream.** tools/retract_lesson.py:43-53 appends updated same-id row, status retracted, then renders MD. render_lessons.py:92-98 appends via locked a+ file. No retraction rewrite patch needed. Recall and renderer dedupe latest same-id state. Retraction permits accepted only, not provisional/legacy; preserve source unless deliberate adaptation needed.

No workflow source-journal rewrite discovered in inspected closure. Rewrites are candidate state or derived views, except maintenance. Specifically:
- graduate appends lesson; mark_graduated mutates/moves candidate only. Retraction append checked above.
- learn episodic mirror opens append at tools/learn.py:85, but does NOT use shared episode lock. Route through common episodic writer or ensure outer stable root lock covers every command.
- render_lessons.py:282 auto-imports legacy below-sentinel bullets; migrate_legacy_bullets appends legacy semantic records. This preserves append-only but is implicit migration during render. Align with agreed explicit migration before exposing on old data.
- graduate.py:87-89 error text suggests manually adding fields to old lesson row; change guidance to supported append-only correction/recovery. Function itself does not overwrite row.
- Maintenance auto_dream does ftruncate/rewrite episodic retained data; keep accessible only maintenance path. Archive moves WORKSPACE; remove active-workspace assumptions.

## Minimal adapter seams, prioritized

1. Shared data/project-root resolver. Preserve package-relative sys.path imports but replace storage constants; BASE currently conflates runtime installation and project data in tools. CLI subprocess learn->graduate must propagate root/config/context, not silently use installed package memory.
2. Preferences/context: context_budget._read ROOT must read consumer AGENTS/permissions and external .agents/PREFERENCES.md; removed working workspace has no replacement active doc. REVIEW_QUEUE relocated explicitly. Note review_state._default_queue_path:82 creates working/ independently of auto_dream.REVIEW_QUEUE constant.
3. Provenance: hooks/_provenance.AGENT_ROOT:4 is script-relative and commit_sha cwd uses it at line60. Redirect to consumer repository to avoid attributing skill repo commit. Cached commit must not leak across roots in multi-root same-process use.
4. Review gate: tools/learn.py defaults to auto-graduate, invents timestamp rationale if omitted (160), reviewer learn.py (166). Wrapper should stage by default or explicitly require reviewed acceptance+rationale, consistent with user-confirmed manual review boundary. Keep maintenance never invoking graduation.
5. Lock: stable root transaction lock shared by every manager/maintenance command; inner semantic lock in render_lessons cannot be naively nested over itself (same-process flock deadlock documented lines56-60). Outer distinct lock path avoids nesting same inode. learn subprocess risks deadlock if parent holds root lock and child reacquires; use in-process graduate or explicit carefully scoped ownership handoff.
6. Atomic maintenance rewrite: upstream ftruncate unsafe on interruption; adapt temp file+atomic replace under stable outer lock. Require all appenders participate, since existing upstream inode locks alone are insufficient across replacement.
7. Search: redirect MEMORY_DIR/INDEX_DIR/INDEX_PATH/FEATURES_PATH; adapt JSONL indexed fields to include semantic claim and effective status handling; invalidate after maintenance. Previously noted source FTS omission is real.
8. Candidate path safety: upstream graduate/review_state concatenate user candidate_id into filename without explicit plain-filename validation in inspected main; preserve local manager candidate id validation in adapter, not arbitrary traversal.

## Verification and limits

Verified exact HEAD, AST import inventory, and targeted source semantics. Hashes above computed from checkout bytes. Source tests not executed. No upstream/cache changes and no consumer memory writes. Only this report created. This is a bounded closure analysis; no scheduler/hook adapter activation or broader stack extraction.
