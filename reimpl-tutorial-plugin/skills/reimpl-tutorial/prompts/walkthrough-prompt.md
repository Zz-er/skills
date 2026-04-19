# Code Walkthrough Prompt — 代码思路拆解
#
# Use this when writing the "代码思路拆解 / Code Walkthrough" section of a
# feature notebook. This section bridges problem/theory → implementation,
# helping readers build a mental model BEFORE seeing real code.

## When to Include a Code Walkthrough

Include when:
- The implementation has 10+ lines of logic
- Multiple functions or classes are involved
- The control flow is non-obvious (branching, loops, callbacks, state)
- The feature manages state (caches, registries, connection pools)
- A reader would stare at the code and ask "but what is actually happening?"
- The feature has no Theory section (Cell 4) — the walkthrough is the ONLY
  bridge between problem and code

Skip ONLY when:
- The implementation is trivially simple (a constant, a one-liner, a simple
  re-export, a thin wrapper that delegates to an existing function)
- The entire feature is 1-2 lines of code

**Litmus test:** If you removed all the code and only had the walkthrough,
could a competent programmer rewrite the implementation? If yes, the
walkthrough is good. If no, it's missing steps.

## Structure of a Good Code Walkthrough

### Opening

```markdown
## 代码思路拆解 / Code Walkthrough

> 在看具体代码之前，我们先用大白话把思路理清楚。
> Before diving into code, let's walk through the logic in plain language.
```

### Section 1 — What Are We Building? (一句话 + 类比)

One sentence summarizing what the code accomplishes in everyday terms,
followed by a real-world analogy:

```markdown
### 我们要做什么？ / What Are We Building?

[One sentence: what this code does, in terms a non-programmer could follow.]

> **类比 / Analogy:** [A familiar process that mirrors the code's workflow.]
```

Good analogies by feature type:
- Config loading: "像填表格 — 必填项不能空，选填项有默认值，填完后锁定不让改"
- Parser: "像翻译官 — 把一种语言逐词翻译成另一种，遇到不认识的词就报错"
- State machine: "像自动售货机 — 投币、选货、出货，每一步只能做特定操作"
- Cache: "像便利贴 — 把常用信息抄在手边，过期了就扔掉重新抄"
- API client: "像打电话 — 拨号、等接通、说话、听回复、挂断"

### Section 2 — Step-by-Step Breakdown (分步拆解)

3-8 numbered steps in plain language. Use "我们" / "we" voice. Each step
should feel like a natural consequence of the previous one:

```markdown
### 分步拆解 / Step-by-Step Breakdown

**Step 1: [Action in plain language]**
[1-3 sentences. "我们先...", "We first check whether..."]

**Step 2: [Action in plain language]**
[Continue the flow. Each step is a natural consequence of the last.]

**Step 3: ...**
```

Rules for steps:
- Describe what *happens* (verbs, actions, data movement), NOT what *exists*
  (class hierarchies, type signatures)
- Wrong: "我们定义一个 ConfigLoader 类，里面有一个 load() 方法"
- Right: "我们读取 YAML 文件，逐个检查字段，把用户没填的用默认值补上，
  最后把整个配置锁定，之后谁也改不了"
- Each step should answer "然后呢？" (and then what?)

### Section 3 — Pseudocode (伪代码) [OPTIONAL]

Include when the logic is intricate (nested loops, multiple branches,
recursive calls). Use **plain pseudocode**, NOT Python:

```markdown
> **伪代码 / Pseudocode:**
> ```
> function process(input):
>     for each item in input:
>         if item matches our criteria:
>             transform it
>             put it in the result bucket
>         else:
>             log a warning and skip
>     return result bucket
> ```
```

The point of pseudocode is to show structure without language-specific
syntax. If you catch yourself writing `def`, `self.`, or `import`, you're
writing Python, not pseudocode.

### Section 4 — Things to Watch For (注意事项)

Edge cases, subtle design decisions, common pitfalls:

```markdown
### 需要注意的地方 / Things to Watch For

- **[Edge case]**: [Why it matters and how we handle it]
- **[Design choice]**: 我们用 X 而不是 Y，因为 [reason]
```

### Section 5 — Data Flow (数据流向) [OPTIONAL]

A one-line pipeline or simple ASCII diagram showing how data moves:

```markdown
### 数据怎么流动？ / How Does Data Flow?

> 原始配置 (dict) → 校验字段 → 合并默认值 → 冻结为不可变对象
> Raw config (dict) → validate fields → merge defaults → freeze as immutable
```

For complex flows, a small ASCII diagram or mermaid block (matching the
tutorial's chosen diagram mode) is appropriate here.

### Section 6 — Mapping to Theory (理论映射) [CONDITIONAL]

Include ONLY when Cell 4 (Theory / Derivation) exists. Explicitly connect
math symbols to the code plan:

```markdown
### 和理论的对应 / Mapping to Theory

- 推导中的 $\phi(x)$ → Step 2 里的 `feature_descriptor()` 函数
- 网格 $\mathcal{B}$ → Step 1 里用 Python dict 实现，key 是 tuple
- 算法第 4 步的选择操作 → Step 3 里的 `select_parent()` 调用
```

---

## The "Three Layers" Pattern — 深入浅出

The best walkthroughs follow a depth progression that embodies 深入浅出
(start shallow and accessible, go deeper with each paragraph):

**Layer 1 — One sentence (一句话概括):**
> "我们要做一个网格，每个格子里放当前最好的方案。"
> "We build a grid that stores the best solution for each niche."

**Layer 2 — Analogy (类比建立直觉):**
> "就像一个分类收纳柜，每个抽屉贴了标签。新方案来了，看标签找到
> 对应抽屉，如果比里面的好就替换，否则扔掉。"

**Layer 3 — Step breakdown (分步详解):**
> The full step-by-step from Section 2 above.

Always write in this order. Never start with the detailed steps — the
reader needs the one-sentence summary and the analogy first to know
where the details are heading.

---

## Bilingual Writing Guidelines — 双语写作

- Use bilingual section headers: "分步拆解 / Step-by-Step Breakdown"
- Chinese text should use conversational register (大白话):
  "我们先看看..." / "简单来说就是..." / "你可以把它想象成..."
- Avoid formal/academic Chinese: not "首先我们需要实例化一个对象", but
  "我们先创建一个..."
- Technical terms: use English in parentheses on first occurrence:
  "特征描述符 (feature descriptor)"、"回调函数 (callback)"
- Analogies work best in Chinese; steps can be bilingual or Chinese-primary

---

## Tone & Voice in Walkthroughs

The walkthrough is where the narrator's personality is most visible. This is
the "knowledgeable friend" zone — Register 2-3 on the formality spectrum
(see `prompts/style-guide.md` §2).

Techniques that work especially well here:
- **Rhetorical questions**: "那问题来了，数据从哪来？" / "So where does the data come from?"
- **Reader empathy**: "看到这里你可能有点懵，没关系" / "If this feels fuzzy, that's normal"
- **Dramatic foreshadowing**: "接下来这一步是关键——搞砸了整个系统就废了"
- **Payoff confirmation**: "（是的，就是这么简单）" / "(yes, it really is that simple)"
- **Colloquial transitions**: "说白了就是..."、"换句话说..." (see `prompts/style-guide.md` §5)

Do NOT put humor in the pseudocode or the data flow diagram — those must be
precise. Humor belongs in the transitions and commentary between technical
content.

See `prompts/style-guide.md` for full voice definition and anti-patterns.

---

## Relationship to Other Notebook Sections

| Section | Answers | Example |
|---------|---------|---------|
| Theory (Cell 4) | "为什么算法有效？" / Why does the math work? | MAP-Elites maintains diversity by... |
| **Walkthrough (Cell 5)** | **"代码会做什么？" / What will the code do?** | **We loop through candidates, compute descriptors, update grid...** |
| Implementation comments | "这一行为什么这样写？" / Why this specific line? | Using dict for O(1) lookup... |

The walkthrough should NOT:
- Duplicate the Theory section's math explanations
- Duplicate the implementation's inline comments
- Describe class hierarchies or type signatures in detail

The walkthrough SHOULD:
- Preview what the inline comments will explain in more detail
- Connect the Theory's symbols to concrete code concepts (when Theory exists)
- Give the reader enough understanding to *predict* what the code will look like

---

## Common Walkthrough Mistakes

1. **Translating code to Chinese ≠ explaining**
   - Bad: "我们定义变量 x，赋值为 5，然后调用 process(x)"
   - Good: "我们先准备好输入数据，然后交给处理器去转换"

2. **Too abstract**
   - Bad: "我们处理数据"
   - Good: "我们把原始的 JSON 配置读进来，逐个字段检查类型是否正确"

3. **Missing the 'why'**
   - Bad: "我们用字典来存储"
   - Good: "我们用字典来存储，因为后面需要按特征快速查找，字典的 O(1) 查找比列表的 O(n) 快得多"

4. **Longer than the code**
   - The walkthrough should be shorter than the implementation it previews
   - Simple features: ~100-150 words / 3-5 steps
   - Complex features: ~300-400 words / 5-8 steps

5. **Using Python syntax in pseudocode**
   - Bad: `def process(self, items: List[Item]) -> Result:`
   - Good: `function process(items) -> result:`

6. **Forgetting the running example**
   - Ground each step in the tutorial's running example:
     "在我们的排序例子里，Step 2 会拿到冒泡排序程序，计算它的
     [速度, 正确率] 特征描述符"

7. **Monotone delivery**
   - Bad: Every step uses the same sentence structure ("We do X. Then we do Y. Then we do Z.")
   - Good: Vary sentence length and structure. Ask a question, then answer it.
     Use short sentences for emphasis after complex explanations. See
     `prompts/style-guide.md` §4.

---

## Examples by Feature Type

### Algorithm Features (MAP-Elites, sorting, search)

Focus on data flow and the core loop. Pseudocode is almost always helpful:

> **Step 1:** 随机生成一批初始方案
> **Step 2:** 对每个方案，计算它的"特征描述符"——用两个数字概括它的特点
> **Step 3:** 把方案放进网格对应的格子里（如果格子空就直接放，有人了就比一比）
> **Step 4:** 从网格里随机挑一个方案，稍微改改，生成新方案
> **Step 5:** 回到 Step 2，重复直到收敛

### Config / Infrastructure Features

Focus on the processing pipeline. "填表格" analogies work well:

> **Step 1:** 读取用户给的配置文件（可能是 YAML、JSON 或命令行参数）
> **Step 2:** 检查必填项有没有漏掉，类型对不对
> **Step 3:** 用户没填的可选项，用我们预设的默认值补上
> **Step 4:** 把最终配置冻结成不可变对象，防止运行时被意外修改

### State Machine / Protocol Features

Focus on states and transitions. A state diagram is very effective here:

> **状态：** 空闲 → 连接中 → 已连接 → 传输中 → 断开
> **Step 1:** 从"空闲"出发，发起连接请求
> **Step 2:** 等对方回应——成功进入"已连接"，超时回到"空闲"并重试
> **Step 3:** 连接建立后开始传输数据
> **Step 4:** 传输完毕或出错，执行清理，回到"空闲"

### Integration Features (API clients, database layers)

Focus on the boundary — what goes in, what comes out, what can go wrong:

> **Step 1:** 把请求参数组装成 API 需要的格式
> **Step 2:** 发送请求，等待响应
> **Step 3:** 检查响应状态——成功就解析数据，失败就分类处理（重试/报错/降级）
> **Step 4:** 把 API 返回的原始数据转换成我们内部的数据结构
