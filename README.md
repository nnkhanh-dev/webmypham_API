# WebMyPham (FastAPI)

Lightweight FastAPI backend scaffold for the WebMyPham project.

Quick start

1. Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
.venv\Scripts\activate    # Windows
python -m pip install -r requirements.txt
```

2. Create a `.env` file in the project root with at least `DATABASE_URL`:

```env
DATABASE_URL=mysql+pymysql://user:password@localhost:3306/webmypham
```

3. Run migrations (project stores migrations under `app/db/migrations`):

```bash
alembic -c app\db\migrations\alembic.ini upgrade head
```

4. Start the dev server:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API

- Main voucher endpoints live at `/vouchers` and return a standardized `BaseResponse` structure.

Notes

- Keep `.env` out of version control. Use `.gitignore` provided in the repo.
- If you need, I can add a `.env.example`, switch pagination to page-based params, or generate initial Alembic migrations.

