# Adding and organizing projects

This repository groups independent learning projects under `projects/`. Follow this guide when adding your next project. Existing projects do not need to be moved into a more complex layout just to match the optional folders below.

## 1. Choose a clear folder name

Use lowercase English words separated by hyphens: `projects/<project-name>/`. Describe the task, not the order in which you created it. Keep the folder name stable because the project index links to it.

## 2. Keep the project self-contained

Every project should have:

- `README.md`: purpose, setup, data source, commands, evaluation, and limitations.
- Source code or a runnable notebook.
- A dependency file appropriate to its tools, such as `requirements.txt` or `pyproject.toml`.
- Tests or a documented validation procedure.

For a small project, source and test files can sit directly beside the README, as in `iris-classifier`. If a project grows, the following layout is a suggestion, not a set of folders to create in advance:

```text
projects/<project-name>/
├── README.md
├── requirements.txt          # Or another dependency manifest
├── src/                      # Optional: reusable code
├── notebooks/                # Optional: exploration and demonstrations
├── tests/                    # Optional: automated tests
├── data/README.md            # Optional: data source and retrieval instructions
└── artifacts/                # Generated outputs; ignored by Git
```

Create optional folders only when there is something to put in them. Keep virtual environments local to the project. Do not add a shared root dependency file unless the repository later gains genuinely shared tooling.

## 3. Document the project

Copy [docs/templates/project-readme.md](docs/templates/project-readme.md) into the project's folder as `README.md`. Replace every placeholder, remove sections that do not apply, and use commands that work from that project's directory.

For datasets, record the original source, access requirements, license or usage terms, feature definitions, and units. Prefer retrieval instructions over committing large or restricted datasets. Small redistributable sample data may be tracked when its purpose and source are documented.

Explain the split between training and test data, preprocessing, baseline, metric definitions, and random seed where relevant. Report only results you actually measured. Separate planned work from completed features.

## 4. Handle generated and local files

The root `.gitignore` excludes Python environments, caches, notebook checkpoints, local environment files, and folders named `artifacts`.

- Store generated models, metrics, and temporary predictions in the project's `artifacts/` folder by default.
- Add a project-specific `.gitignore` if a tool needs other local output folders. Avoid broad root rules that could hide useful sample data in other projects.
- Never commit credentials, private records, or datasets you cannot redistribute.
- If a small evaluation summary is useful to readers, include it in the README or a clearly named report, separate from bulk generated output.
- Restart notebooks and run all cells in order before publishing; review their outputs for private information and unnecessary bulk.

## 5. Update the project index

Add one row to the table in the root [README.md](README.md). Include the project link, task, main tools, and an honest status such as `In progress` or `Working demo`. Do not list placeholder projects.

## Before pushing

- [ ] The project is entirely inside its own `projects/<name>/` folder.
- [ ] The README has no unfilled template placeholders.
- [ ] Setup and run commands were checked in the documented environment.
- [ ] Dependencies and dataset instructions are included.
- [ ] Tests or the documented validation procedure pass.
- [ ] Evaluation notes describe the data split and limitations where applicable.
- [ ] Generated files, credentials, and restricted data are excluded.
- [ ] The root project-index link points to the correct folder.

## خلاصهٔ دری

برای هر پروژه یک پوشهٔ مستقل بسازید. راهنمای اجرا، وابستگی‌ها، منبع داده‌ها و روش ارزیابی را در همان پوشه بنویسید. پوشه‌های اختیاری را تنها در صورت نیاز ایجاد کنید. پیش از پوش کردن، اجرای پروژه و لینک آن در جدول اصلی را بررسی نمایید و فایل‌های تولیدشده یا معلومات خصوصی را وارد مخزن نکنید.
