import os
import re
import pandas as pd
from sqlalchemy import create_engine
from colorama import Fore, Style, init
from jinja2 import Environment, FileSystemLoader
from datetime import datetime
from dotenv import load_dotenv
import yaml

class SQL_TO_LATEX:
    def __init__(self, working_folder, data_access, queries_folder):
        self.working_folder = working_folder
        self.data_access = data_access 
        self.queries_folder = queries_folder
        self.template_file = os.path.join('.', 'Templates', 'main_report.tex') # Root, templates. 
        self.output_folder = os.path.join(self.working_folder, 'Reportes BI')

    def sql_conexion(self):
        sql_url = self.data_access['sql_url']
        #url example: 'postgresql://arXXXrge:XXX@ep-shy-darkness-10211313-poolXXXX.tech/neondb?sslmode=require&channel_binding=require'
        try:
            engine = create_engine(sql_url)
            return engine
        except Exception as e:
            print(f"❌ Error connecting to database: {e}")
            return None
        
    def sql_to_dataframe(self): 
        engine = self.sql_conexion()  # must return a SQLAlchemy Engine
        if engine is None:
            print("❌ No se pudo obtener el engine de SQL.")
            return False
        dataframes = {}
        for file in os.listdir(self.queries_folder):
            if file.endswith(".sql"):
                name = os.path.splitext(file)[0]
                print(f"{name}")
                with open(os.path.join(self.queries_folder, file)) as f:
                    query = f.read()
                df = pd.read_sql(query, engine)
                dataframes[name] = df
        print(f"{Fore.GREEN} Extracción de dataframes finalizada. {Style.RESET_ALL}")
        return dataframes

    def generate_report(self, dataframes):
        if not dataframes:
            print("No hay dataframes disponibles para el reporte.")
            return None

        escape_map = {
            "\\": r"\textbackslash{}",
            "&": r"\&",
            "%": r"\%",
            "$": r"\$",
            "#": r"\#",
            "_": r"\_",
            "{": r"\{",
            "}": r"\}",
            "~": r"\textasciitilde{}",
            "^": r"\textasciicircum{}",
        }
        escape_pattern = re.compile("|".join(re.escape(key) for key in escape_map))

        def _format_value(value):
            if pd.isna(value):
                return ""
            if isinstance(value, float):
                if value.is_integer():
                    value = int(value)
                return f"{value:.2f}".rstrip("0").rstrip(".")
            text = str(value).replace('\t', ' ').strip()
            return escape_pattern.sub(lambda match: escape_map[match.group()], text)

        latex_tables = {}
        for name, df in dataframes.items():
            if df.empty:
                latex_tables[name] = "\\begin{center}\\textit{Sin datos disponibles}\\end{center}"
                continue
            sanitized_df = df.copy()
            sanitized_df = sanitized_df.map(_format_value)
            sanitized_df.columns = [_format_value(col) for col in sanitized_df.columns]
            caption = name.replace('_', ' ').title()
            latex_tables[name] = sanitized_df.to_latex(index=False, longtable=True, escape=False, na_rep="", caption=caption, label=f"tab:{name}")

        # Build the LaTeX document dynamically
        rendered_tex = (
            "\\documentclass{article}\n"
            "\\usepackage{booktabs}\n"
            "\\usepackage{longtable}\n"
            "\\begin{document}\n\n"
        )
        for name, table in latex_tables.items():
            section_name = name.replace('_', ' ').title()
            rendered_tex += f"\\section*{{{section_name}}}\n{table}\n\n"
        rendered_tex += "\\end{document}"

        os.makedirs(self.output_folder, exist_ok=True)
        output_filename = datetime.now().strftime('%Y%m%d_%H%M%S_report.tex')
        output_path = os.path.join(self.output_folder, output_filename)
        with open(output_path, 'w', encoding='utf-8') as tex_file:
            tex_file.write(rendered_tex)
        return output_path

    def reporting_latex_run(self):
        print(f"{Fore.CYAN}\t⚡ Ejecutando consultas SQL para generación de reportes LaTeX...{Style.RESET_ALL}")
        dataframes = self.sql_to_dataframe()
        for key, value in dataframes.items(): 
            print(key)
            print(value.head())
        self.generate_report(dataframes)
        print(f"{Fore.GREEN}\t✅ Reportes LaTeX generados exitosamente.{Style.RESET_ALL}")

if __name__ == "__main__":
    # Set working folder
    script_dir = os.path.dirname(os.path.abspath(__file__))
    root = os.path.abspath(os.path.join(script_dir, ".."))
    env_file = os.path.join(root, ".env")
    # 1. Load .env if it exists
    if os.path.exists(env_file):
        load_dotenv(env_file)
    folder_root = os.getenv("MAIN_PATH")
    working_folder = os.path.join(folder_root, "Local Data")
    # Set the dict with sql URL
    yaml_path = os.path.join(working_folder, "config.yaml")
    yaml_exists = os.path.exists(yaml_path)
    integration_path = os.path.join(working_folder, "Integración")
    if yaml_exists:
        # Abrir y cargar el contenido YAML en un diccionario
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data_access = yaml.safe_load(f)
        print(f"✅ Archivo YAML cargado correctamente: {os.path.basename(yaml_path)}")   

    # Set queries folder
    queries_folder = os.path.join(root, "sql_queries")
    # Initialize and run
    app = SQL_TO_LATEX(working_folder, data_access, queries_folder)
    app.reporting_latex_run()