# Content Modules

Each subfolder inside `modules/` can provide one learning module.

Minimum structure:

```text
modules/
  my_module/
    module.py
```

or:

```text
modules/
  my_module/
    module.json
```

`module.py` should expose either:

- `MODULE = {...}`
- or `build_module() -> dict`

`module.json` can contain the same payload in plain JSON.

Required top-level fields:

- `id`: stable DB/sphere id
- `slug`: module slug
- `sort_order`
- `title_ru`, `title_pl`, `title_en`
- `description_ru`, `description_pl`, `description_en`
- `levels`: list
- `topics`: list

Topic fields:

- `id`
- `slug`
- `mode`
- `grade`
- `theme`
- `sort_order`
- `title_ru`, `title_pl`, `title_en`
- `description_ru`, `description_pl`, `description_en`
- `lessons`
- `tasks`

Lesson fields:

- `title_ru`, `title_pl`, `title_en`
- `content_ru`, `content_pl`, `content_en`

Task fields match the current app task format:

- `id`
- `type`
- `mode`
- `grade`
- `theme`
- `title_ru`, `title_pl`
- `prompt_ru`, `prompt_pl`
- `answer`
- `options`
- `hint_type`
- optional `metadata`

The app syncs module content from disk into the local database on startup.
Module-managed lessons and tasks are treated as the source of truth from the folder.
If you remove a module folder, its module-managed topics disappear from the app on the next start.

You can now add new modules in two ways:

- copy a ready folder into `modules/`
- use the import buttons in the parent settings panel for folder / zip / JSON import

Starter JSON templates are available in `module_templates/`.
