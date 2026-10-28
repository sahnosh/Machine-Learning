# Machine Learning

A collection of independent machine learning projects, experiments, and notebooks. Each project lives in its own folder with its own dependencies, setup instructions, and evaluation notes.

## Repository structure

```text
Machine-Learning/
├── README.md                         # Overview and project index
├── CONTRIBUTING.md                   # How to add and document a project
├── .gitignore                        # Shared exclusions for local/generated files
├── docs/
│   └── templates/
│       └── project-readme.md          # Reusable documentation template
└── projects/
    └── iris-classifier/              # Existing Iris classification project
```

## Projects

| Project | Task | Tools | Status |
| --- | --- | --- | --- |
| [Iris Flower Classifier](projects/iris-classifier/) | Predict one of three Iris species from four flower measurements | Python, scikit-learn | Working demo |

Open a project's README for its installation, training, prediction, and testing commands. Run those commands from that project's folder.

## Adding a project later

1. Create `projects/<short-descriptive-name>/`, using lowercase words separated by hyphens.
2. Copy the [project README template](docs/templates/project-readme.md) into that folder as `README.md` and replace the placeholders.
3. Keep that project's code, dependencies, notebooks, and tests inside its folder.
4. Add one row to the project index above, linking to the new folder.

See [CONTRIBUTING.md](CONTRIBUTING.md) for the recommended layout and checklist. The template is documentation only; it is not an additional project.

## Organization principles

- One project per folder; use descriptive names such as `iris-classifier` rather than `project1` or `final-version`.
- Keep dependency environments separate so one project's packages do not affect another.
- Document dataset sources, evaluation methods, and limitations in each project.
- Keep generated models, large datasets, private information, and local environments out of Git.
- Add projects to the index only when their folders actually exist.

## راهنمای کوتاه دری

هر پروژه در یک پوشهٔ جداگانه داخل `projects/` نگهداری می‌شود. برای افزودن پروژهٔ بعدی، یک نام کوتاه انگلیسی با حروف کوچک و خط تیره انتخاب کنید، قالب راهنما را از `docs/templates/project-readme.md` کاپی کنید و یک سطر به جدول پروژه‌ها اضافه نمایید. وابستگی‌ها و فایل‌های هر پروژه را در همان پوشه نگه دارید.
