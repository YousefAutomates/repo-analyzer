<div align="center">

<!-- LOGO / BANNER -->
<h1>🔍 GitHub Repository Analyzer</h1>

<p align="center">
  <strong>Analyze any GitHub repository and generate a comprehensive AI-ready report in seconds.</strong>
</p>

<p align="center">
  <em>One command. Full codebase. Ready for AI.</em>
</p>

<!-- BADGES -->
<p align="center">
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/Python-3.7+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python"/>
  </a>
  <a href="https://colab.research.google.com/">
    <img src="https://img.shields.io/badge/Google_Colab-Ready-F9AB00?style=for-the-badge&logo=google-colab&logoColor=white" alt="Colab"/>
  </a>
  <a href="https://www.kaggle.com/">
    <img src="https://img.shields.io/badge/Kaggle-Ready-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white" alt="Kaggle"/>
  </a>
  <a href="LICENSE">
    <img src="https://img.shields.io/badge/License-MIT-green?style=for-the-badge" alt="License"/>
  </a>
  <a href="https://github.com/YousefAutomates/repo-analyzer/releases">
    <img src="https://img.shields.io/badge/Version-2.0.0-blue?style=for-the-badge" alt="Version"/>
  </a>
</p>

<!-- LANGUAGE TOGGLE -->
<p align="center">
  <a href="#-english-documentation">
    <img src="https://img.shields.io/badge/🇬🇧_English-Documentation-blue?style=for-the-badge" alt="English"/>
  </a>
  &nbsp;&nbsp;
  <a href="#-التوثيق-بالعربي">
    <img src="https://img.shields.io/badge/🇸🇦_عربي-التوثيق-green?style=for-the-badge" alt="Arabic"/>
  </a>
</p>

<br/>

<!-- HERO DESCRIPTION -->
<table>
<tr>
<td>

**Stop manually copying files to share with AI.** This tool scans any GitHub repository and creates a single, well-structured text file containing the entire codebase — perfectly formatted for ChatGPT, Claude, Gemini, and other AI assistants.

**بطّل تنسخ الملفات واحد واحد.** الأداة دي بتحلل أي مستودع على GitHub وبتطلعلك ملف واحد فيه كل الأكواد — جاهز تبعته للذكاء الاصطناعي مباشرة.

</td>
</tr>
</table>

</div>

---

# 🇬🇧 English Documentation

## ⚡ Quick Start

**One command** — works in Google Colab, Kaggle, or any terminal:

```python
!git clone https://github.com/YousefAutomates/repo-analyzer.git && cd repo-analyzer && pip install -q -r requirements.txt && python run.py
```

That's it. The tool will guide you through the rest interactively.

---

## 🎯 What Does This Tool Do?

This tool **scans any GitHub repository** and generates a **single comprehensive TXT file** containing:

| Section | What's Included |
|---------|----------------|
| 📋 **Repository Info** | Name, description, stars, forks, license, topics, visibility |
| 🌳 **Project Structure** | Complete visual directory tree |
| 📊 **Statistics** | Total lines of code, file sizes, language breakdown |
| 📦 **Dependencies** | Parsed from requirements.txt, package.json, go.mod, etc. |
| 📄 **ALL Source Code** | Full content of every text file with syntax highlighting |
| 👥 **Contributors** | Who contributed and how many commits |
| 📝 **Commit History** | Latest changes with authors and dates |
| 🤖 **AI Token Estimate** | Shows compatibility with GPT-4, Claude, Gemini context windows |
| 📌 **AI Prompt Template** | Ready-to-use instructions for your AI request |

---

## 💡 Why Use This?

### The Problem
When you want AI to **understand, modify, or build upon** an existing project, you need to share the **complete codebase**. Manually copying dozens of files is:
- ⏰ **Time-consuming** — especially for large projects
- 😵 **Error-prone** — you might miss important files
- 🔀 **Unstructured** — AI loses context without proper organization
- 📏 **Uncertain** — you don't know if it fits the AI's context window

### The Solution
This tool does everything **automatically** in seconds:
```
1. 🔍 Run the analyzer on any GitHub repo
2. 📄 Get a single, perfectly structured TXT file
3. 📋 Copy and paste into your AI assistant
4. 💬 Add your request (modify, explain, fix, improve)
5. ✨ Get AI-powered results!
```

---

## 🌟 Key Features

### 🔐 Security
| Feature | Description |
|---------|-------------|
| 🔑 **Secure Token Input** | Token is hidden when you type (uses `getpass`) |
| 🌍 **Environment Variables** | Supports `GITHUB_TOKEN` env variable |
| 🧹 **Memory Cleanup** | Token is cleared from memory after use |
| ✅ **Permission Check** | Validates token scopes before scanning |

### 🛡️ Reliability
| Feature | Description |
|---------|-------------|
| 🔄 **Auto Retry** | Automatically retries failed API requests (3 attempts) |
| ⏳ **Rate Limit Handling** | Detects rate limits and waits automatically |
| 🌐 **Connection Recovery** | Handles network timeouts gracefully |
| ⚠️ **Error Messages** | Clear, helpful error messages for every situation |

### 📊 Smart Analysis
| Feature | Description |
|---------|-------------|
| 🧮 **Token Estimation** | Estimates token count for AI context windows |
| 📦 **Dependency Parsing** | Analyzes requirements.txt, package.json, go.mod, etc. |
| 🚫 **Smart Filtering** | Automatically skips node_modules, __pycache__, .git, etc. |
| 📏 **Size Limits** | Configurable max file size (default 500KB) |
| 🏷️ **File Categorization** | Groups files by language/type |

### 🖥️ User Experience
| Feature | Description |
|---------|-------------|
| ⚡ **Smart Defaults** | Optimal settings out of the box — just press Enter |
| 📂 **3 Modes** | Public repo, private repo, or browse your repos |
| 🌿 **Branch Selection** | Analyze any branch, not just main |
| 🔍 **Repo Browser** | Search, filter, and paginate through your repos |
| ⬇️ **Auto Download** | File downloads automatically in Colab/Kaggle |

### 🤖 AI Compatibility
| AI Model | Context Window | Status |
|----------|---------------|--------|
| GPT-3.5 Turbo | 16K tokens | ✅ Small projects |
| GPT-4 / GPT-4o | 128K tokens | ✅ Most projects |
| Claude 3.5 Sonnet | 200K tokens | ✅ Large projects |
| Gemini 1.5/2.0 | 1M tokens | ✅ Very large projects |

---

## 📖 Usage Guide

### Mode 1: Analyze a Public Repository (No Token)

```
Choice: 1
Repository: facebook/react
```

That's it! No authentication needed for public repos.

### Mode 2: Analyze a Private Repository

```
Choice: 2
Token: ghp_xxxxxxxxxxxx (hidden input)
Repository: mycompany/private-api
```

### Mode 3: Browse & Select Your Repos

```
Choice: 3
Token: ghp_xxxxxxxxxxxx (hidden input)
→ Shows your repos with search, filter, and pagination
→ Select by number
```

---

## 🔑 Creating a GitHub Token

1. Go to [github.com/settings/tokens](https://github.com/settings/tokens)
2. Click **"Generate new token (classic)"**
3. Give it a name (e.g., "repo-analyzer")
4. Select scopes:
   - ✅ `repo` — Full control (required for private repos)
   - ✅ `read:user` — Read user info (optional)
5. Click **"Generate token"**
6. **Copy the token immediately** (you won't see it again!)

> 💡 **Tip:** For public repos only, you don't need a token at all!

> 💡 **Tip:** You can set the `GITHUB_TOKEN` environment variable to skip the input prompt.

---

## 🤖 Using the Report with AI

### Step 1: Generate the Report
Run the tool and get your TXT file.

### Step 2: Send to AI
Open the TXT file, copy ALL content, and paste it into your AI assistant.

### Step 3: Add Your Request
After pasting, add your specific request:

```
I've shared my complete project above. Please:

1. Explain how the authentication flow works
2. Find any security vulnerabilities
3. Add rate limiting to the API endpoints
4. Write unit tests for the user module
5. Suggest performance improvements

Please provide the modified code for each change.
```

### 💡 Creative Use Cases

| Use Case | Description |
|----------|-------------|
| 🔍 **Code Review** | Ask AI to review the entire codebase for bugs and improvements |
| 📝 **Documentation** | Generate comprehensive docs from the code |
| 🔒 **Security Audit** | Find vulnerabilities and security issues |
| 🧪 **Test Generation** | Auto-generate unit tests for all modules |
| 🔄 **Language Conversion** | Convert a Python project to JavaScript (or vice versa) |
| 📚 **Learning** | Understand how an open-source project works |
| 👋 **Onboarding** | Help new developers understand the codebase quickly |
| 🏗️ **Architecture Review** | Get AI feedback on project structure and design patterns |
| 📊 **Comparison** | Generate reports for 2 projects and ask AI to compare them |
| ♻️ **Refactoring** | Get suggestions for cleaner, more maintainable code |

---

## 📁 Project Structure

```
repo-analyzer/
├── run.py                      # Entry point with dependency management
├── requirements.txt            # Python dependencies
├── LICENSE                     # MIT License
├── README.md                   # This file
├── .gitignore                  # Git ignore rules
└── analyzer/                   # Main package
    ├── __init__.py             # Package init (version info)
    ├── github_client.py        # GitHub API client with retry & rate limiting
    ├── repo_scanner.py         # Repository scanning & file analysis
    ├── report_generator.py     # AI-ready report generation
    ├── file_exporter.py        # TXT export with auto-download
    └── main.py                 # Interactive CLI application
```

---

## ⚙️ Configuration

### Default Settings (Optimal)

| Setting | Default | Description |
|---------|---------|-------------|
| Output Format | TXT | Best for AI consumption |
| Max File Size | 500 KB | Skip files larger than this |
| Max Files | 500 | Limit total files to scan |
| Include Contents | Yes | Include full source code |
| Include Stats | Yes | Include statistics section |
| Include Commits | Yes | Include commit history |
| Include Contributors | Yes | Include contributors list |
| Auto Download | Yes | Download file in Colab/Kaggle |

### Skipped Directories (Automatic)

These directories are automatically excluded from scanning:

```
node_modules/    __pycache__/    .git/           vendor/
venv/            dist/           build/          .idea/
.vscode/         coverage/       .tox/           .terraform/
```

### Environment Variables

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | GitHub personal access token (skips input prompt) |

---

## 🛠️ Technical Details

### Architecture

```
┌─────────────────────────────────────────────────┐
│                  RepoAnalyzerApp                │
│                   (main.py)                     │
│            Interactive CLI Interface            │
├─────────┬──────────┬─────────────┬──────────────┤
│ GitHub  │   Repo   │   Report    │    File      │
│ Client  │ Scanner  │ Generator   │  Exporter    │
│         │          │             │              │
│ • Auth  │ • Tree   │ • Header    │ • TXT Export │
│ • Retry │ • Filter │ • Stats     │ • Auto-DL    │
│ • Rate  │ • Scan   │ • Code      │ • Colab      │
│ • API   │ • Stats  │ • Tokens    │ • Kaggle     │
└─────────┴──────────┴─────────────┴──────────────┘
```

### API Rate Limits

| Authentication | Rate Limit |
|---------------|------------|
| No token | 60 requests/hour |
| With token | 5,000 requests/hour |

> The tool automatically handles rate limiting. If you hit the limit, it will wait and retry.

### Dependencies

| Package | Purpose |
|---------|---------|
| `requests` | HTTP requests to GitHub API |
| `rich` | Enhanced terminal output (optional) |

---

## ❓ FAQ

<details>
<summary><b>Can I analyze private repositories?</b></summary>

Yes! Use Mode 2 or Mode 3 with a GitHub token that has `repo` scope.
</details>

<details>
<summary><b>What if the repo is too large for AI?</b></summary>

The tool shows token estimates and compatibility with each AI model. For very large repos, consider:
- Reducing max file size
- The tool automatically skips binary files and common junk directories
- Use a model with a larger context window (Gemini 1.5 Pro supports 1M tokens)
</details>

<details>
<summary><b>Is my token safe?</b></summary>

Yes. The token is:
- Hidden during input (not displayed on screen)
- Cleared from memory after the scan completes
- Never stored to disk or logged
- You can also use the `GITHUB_TOKEN` environment variable
</details>

<details>
<summary><b>What file formats are supported?</b></summary>

The tool generates TXT files, which are the most compatible format for AI assistants. The report includes markdown-style code blocks with syntax highlighting hints.
</details>

<details>
<summary><b>Can I use this on my local machine?</b></summary>

Yes! Clone the repo and run `python run.py` in your terminal. It works on Windows, macOS, and Linux.
</details>

<details>
<summary><b>Does it work with GitLab or Bitbucket?</b></summary>

Currently, only GitHub repositories are supported. GitLab and Bitbucket support is planned for future versions.
</details>

---

## 🗺️ Roadmap

- [x] Core repository scanning
- [x] AI-ready TXT report generation
- [x] Token estimation & AI compatibility check
- [x] Dependency analysis
- [x] Secure token handling
- [x] Auto retry & rate limit handling
- [x] Smart directory filtering
- [x] Auto-download in Colab/Kaggle
- [ ] Local repository analysis (without GitHub)
- [ ] Markdown report format
- [ ] Custom ignore patterns (.analyzerignore)
- [ ] GitLab & Bitbucket support
- [ ] Command-line arguments (non-interactive mode)
- [ ] Report splitting for very large repos
- [ ] Web interface (Streamlit)
- [ ] Direct AI API integration
- [ ] VS Code extension
- [ ] GitHub Action

---

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. 🍴 Fork this repository
2. 🌿 Create a feature branch (`git checkout -b feature/amazing-feature`)
3. 💾 Commit your changes (`git commit -m 'Add amazing feature'`)
4. 📤 Push to the branch (`git push origin feature/amazing-feature`)
5. 🔄 Open a Pull Request

---

## 📄 License

This project is licensed under the **MIT License** — see the [LICENSE](LICENSE) file for details.

---

<br/>
<br/>

---

# 🇸🇦 التوثيق بالعربي

<div dir="rtl">

## ⚡ البداية السريعة

**أمر واحد** — يشتغل في Google Colab أو Kaggle أو أي Terminal:

```python
!git clone https://github.com/YousefAutomates/repo-analyzer.git && cd repo-analyzer && pip install -q -r requirements.txt && python run.py
```

وبس كده! الأداة هتوجهك خطوة بخطوة.

---

## 🎯 إيه اللي بتعمله الأداة دي؟

الأداة بتعمل **تحليل شامل لأي مستودع على GitHub** وبتطلع **ملف TXT واحد** فيه كل حاجة:

| القسم | المحتوى |
|-------|---------|
| 📋 **معلومات المستودع** | الاسم والوصف والنجوم والفوركات والرخصة والتوبيكات |
| 🌳 **هيكل المشروع** | شجرة المجلدات والملفات كاملة |
| 📊 **إحصائيات** | عدد أسطر الكود وأحجام الملفات واللغات المستخدمة |
| 📦 **المكتبات** | تحليل requirements.txt و package.json وغيرهم |
| 📄 **كل الأكواد** | محتوى كل ملف كود بالكامل مع تنسيق syntax |
| 👥 **المساهمين** | مين ساهم وبكام commit |
| 📝 **سجل التعديلات** | آخر التعديلات بالمؤلف والتاريخ |
| 🤖 **تقدير التوكنات** | هل الملف هيدخل في GPT-4 ولا Claude ولا Gemini |
| 📌 **قالب للـ AI** | تعليمات جاهزة تكتب فيها طلبك |

---

## 💡 ليه تستخدم الأداة دي؟

### المشكلة
لما تحب تطلب من الذكاء الاصطناعي يفهم أو يعدّل مشروع، محتاج تبعتله **كل الأكواد**. نسخ الملفات واحد واحد:
- ⏰ **بياخد وقت كتير** — خصوصاً المشاريع الكبيرة
- 😵 **ممكن تنسى ملفات** — وتضيع السياق
- 🔀 **مش منظم** — الـ AI مش هيفهم بدون تنظيم
- 📏 **مش متأكد** — هل الكود هيدخل في context الـ AI ولا لأ

### الحل
الأداة دي بتعمل كل ده **أوتوماتيك** في ثواني:
```
1. 🔍 شغّل الأداة على أي ريبو
2. 📄 هتاخد ملف TXT واحد منظم
3. 📋 انسخ المحتوى في ChatGPT / Claude / Gemini
4. 💬 اكتب طلبك (عدّل، اشرح، صلّح، حسّن)
5. ✨ خد النتيجة!
```

---

## 🌟 المميزات الرئيسية

### 🔐 الأمان
- 🔑 **التوكن مخفي** — مش بيظهر وأنت بتكتبه
- 🌍 **Environment Variable** — ممكن تحط التوكن في متغير بيئة
- 🧹 **تنظيف الذاكرة** — التوكن بيتمسح بعد الاستخدام

### 🛡️ الموثوقية
- 🔄 **إعادة المحاولة** — لو الاتصال فشل بيحاول 3 مرات
- ⏳ **Rate Limit** — بيستنى تلقائياً لو وصل للحد الأقصى
- 🌐 **استقرار** — بيتعامل مع مشاكل الشبكة بذكاء

### 📊 تحليل ذكي
- 🧮 **تقدير التوكنات** — بيحسبلك هل الملف هيدخل في الـ AI ولا لأ
- 📦 **تحليل المكتبات** — بيقرأ requirements.txt و package.json
- 🚫 **فلترة ذكية** — بيتجاهل node_modules و __pycache__ تلقائياً

### 🖥️ سهولة الاستخدام
- ⚡ **إعدادات مثالية** — بس اضغط Enter وهو يشتغل
- 📂 **3 أوضاع** — ريبو عام أو خاص أو تصفح ريبوزاتك
- ⬇️ **تحميل تلقائي** — الملف بينزل أوتوماتيك في Colab

---

## 🔑 إنشاء توكن GitHub

1. روح على [github.com/settings/tokens](https://github.com/settings/tokens)
2. اضغط **"Generate new token (classic)"**
3. سمّيه (مثلاً "repo-analyzer")
4. اختار الصلاحيات:
   - ✅ `repo` — تحكم كامل (لازم للريبوز الخاصة)
5. اضغط **"Generate token"**
6. **انسخ التوكن فوراً** (مش هيظهرلك تاني!)

> 💡 للريبوز العامة مش محتاج توكن خالص!

---

## 🤖 الاستخدام مع الذكاء الاصطناعي

### الخطوة 1: ولّد التقرير
شغّل الأداة وخد ملف الـ TXT.

### الخطوة 2: ابعت للـ AI
افتح الملف وانسخ كل المحتوى والصقه في ChatGPT أو Claude أو Gemini.

### الخطوة 3: اكتب طلبك
بعد ما تلصق المحتوى، اكتب اللي عاوزه:

```
ده مشروعي الكامل بكل الأكواد. عاوز:

1. اشرحلي إزاي الـ authentication بيشتغل
2. دوّر على أي مشاكل أمنية
3. أضف rate limiting للـ API
4. اكتبلي unit tests للـ user module
5. اقترح تحسينات للأداء

اديني الكود المعدّل لكل تغيير.
```

### 💡 استخدامات إبداعية

| الاستخدام | الوصف |
|-----------|-------|
| 🔍 **مراجعة الكود** | الـ AI يراجعلك الكود كله ويلاقي الأخطاء |
| 📝 **توثيق تلقائي** | يولّدلك documentation كاملة من الكود |
| 🔒 **فحص أمني** | يدوّر على الثغرات الأمنية |
| 🧪 **كتابة Tests** | يكتبلك unit tests لكل الموديولات |
| 🔄 **تحويل اللغة** | يحوّلك المشروع من Python لـ JavaScript أو العكس |
| 📚 **تعلّم** | يشرحلك إزاي مشروع open source بيشتغل |
| 👋 **Onboarding** | يساعد المطورين الجدد يفهموا الكود بسرعة |
| 🏗️ **مراجعة معمارية** | يديك رأيه في بنية المشروع |
| ♻️ **Refactoring** | يقترح كود أنظف وأسهل في الصيانة |

---

## ❓ أسئلة شائعة

<details>
<summary><b>هل يقدر يحلل ريبوز خاصة؟</b></summary>

أيوا! استخدم الوضع 2 أو 3 مع توكن GitHub عنده صلاحية `repo`.
</details>

<details>
<summary><b>لو الريبو كبير أوي؟</b></summary>

الأداة بتعرض تقدير التوكنات وتوافق كل AI. للريبوز الكبيرة جداً:
- الأداة بتتجاهل الملفات الثنائية والمجلدات الغير مهمة تلقائياً
- ممكن تقلل حجم الملف الأقصى
- استخدم Gemini 1.5 Pro (بيدعم مليون توكن)
</details>

<details>
<summary><b>هل التوكن بتاعي آمن؟</b></summary>

أيوا! التوكن:
- مش بيظهر على الشاشة وأنت بتكتبه
- بيتمسح من الذاكرة بعد الاستخدام
- مش بيتحفظ على الهارد ولا بيتسجل في أي log
</details>

<details>
<summary><b>بيشتغل على GitLab أو Bitbucket؟</b></summary>

حالياً بيدعم GitHub بس. دعم GitLab و Bitbucket مخطط في النسخ القادمة.
</details>

---

## 🗺️ خطة المستقبل

- [x] تحليل المستودعات الأساسي
- [x] تقرير TXT جاهز للـ AI
- [x] تقدير التوكنات والتوافق
- [x] تحليل المكتبات
- [x] أمان التوكن
- [x] إعادة المحاولة التلقائية
- [x] فلترة المجلدات الذكية
- [x] تحميل تلقائي في Colab/Kaggle
- [ ] تحليل مستودعات محلية
- [ ] تقرير بصيغة Markdown
- [ ] أنماط تجاهل مخصصة (.analyzerignore)
- [ ] دعم GitLab و Bitbucket
- [ ] وضع سطر الأوامر (بدون تفاعل)
- [ ] تقسيم التقارير الكبيرة
- [ ] واجهة ويب (Streamlit)
- [ ] ربط مباشر مع API الذكاء الاصطناعي
- [ ] إضافة VS Code
- [ ] GitHub Action

---

## 📄 الرخصة

المشروع مرخّص تحت **رخصة MIT** — شوف ملف [LICENSE](LICENSE) للتفاصيل.

</div>

---

<div align="center">

<br/>

## 👤 About the Author

<table>
<tr>
<td align="center">

**Yousef Elsherbiny**

*Automation & AI Solutions*

[![Website](https://img.shields.io/badge/🌐_Website-yousefautomates.pages.dev-blue?style=for-the-badge)](https://yousefautomates.pages.dev)
[![GitHub](https://img.shields.io/badge/GitHub-YousefAutomates-181717?style=for-the-badge&logo=github)](https://github.com/YousefAutomates)

</td>
</tr>
</table>

<br/>

---

**Built with ❤️ by [YousefAutomates](https://yousefautomates.pages.dev)**

⭐ **If this tool saved you time, please star the repo!** ⭐

<br/>

<a href="https://github.com/YousefAutomates/repo-analyzer">
  <img src="https://img.shields.io/github/stars/YousefAutomates/repo-analyzer?style=social" alt="Stars"/>
</a>

</div>
