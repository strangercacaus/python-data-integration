from setuptools import setup, find_packages

setup(
    name="python-data-integration",
    version="0.1.0",
    packages=find_packages(where='src'),  # Specify the source directory
    package_dir={'': 'src'},  # Set the root package directory
    install_requires=[
        "psycopg2-binary",
        "sql-metadata>=2.7.0",
        "SQLAlchemy",
        "sqlparse==0.5.0",
        "Unidecode==1.3.8",
        "pyyaml==6.0.2",
        "discord==2.3.2",
        "ratelimit==2.2.1",
        "python-dotenv==1.0.0",
        "numpy==1.26.4",
        "pandas==2.1.4",
        "pytz==2025.2",
        "tzdata==2025.2",
        "requests==2.31.0",
        "jinja2>=3.1.3,<4",
        "python-dotenv==1.0.0",
        "protobuf",
        "dbt_core",
        "dbt_postgres",
        "dbt-extractor",
        "dbt-semantic-interfaces"
    ],
    author="Cauê Marchionatti Ausec",
    author_email="caue.ausec@gmail.com",
    description="A data integration library for ETL pipelines",
    long_description=open("readme.md").read(),
    long_description_content_type="text/markdown",
    python_requires=">=3.10",
)