import os
import re   
from dotenv import load_dotenv
import yaml
from typing import Dict, List, Optional
from datetime import date
from Scripts.latex_generation import SQL_TO_LATEX as LatexGen

class SQL_TO_LATEX:

    def __init__(self) -> None:
        self.folder_root = self.load_default_path()
        self.working_folder = os.path.join(self.folder_root, "Local Data")
        os.makedirs(self.working_folder, exist_ok=True)
        self.yaml_path = os.path.join(self.working_folder, "config.yaml")
        self.data_access = self._load_variables(self.yaml_path)
        self.today = date.today()
        self.queries_folder = os.path.join(self.folder_root, "sql_queries")
        self.latex_generation = LatexGen(self.working_folder, self.data_access, self.queries_folder)
        self.template_file = os.path.join('.', 'Templates', 'main_report.tex') # Root, templates. 
        self.output_folder = os.path.join(self.working_folder, 'Reportes BI')
        
    def menu(self):
        print("\nMenu Options:")
        print("1. SQL to Markdown")

        user_choice = input("Select an option: ").strip()
        if user_choice == "1":
            self.latex_generation.reporting_latex_run()

        else:
            print("Invalid option. Please try again.")
        return

    def load_default_path(self):
        """
        Loads MAIN_PATH from .env or creates .env with current working directory if not found.
        Ensures .env is in .gitignore.
        Returns the resolved path.
        """
        env_file = ".env"
        gitignore_file = ".gitignore"

        # 1. Load .env if it exists
        if os.path.exists(env_file):
            load_dotenv(env_file)

        main_path = os.getenv("MAIN_PATH")

        # 2. If .env or MAIN_PATH not defined, create with current path
        if not main_path or not os.path.exists(main_path):
            current_path = os.getcwd()
            with open(env_file, "w") as f:
                f.write(f"MAIN_PATH={current_path}\n")
            print(f"⚙️  .env file created with default MAIN_PATH={current_path}")
            print("\tIf you want to set a different path, edit the .env file manually.")
            main_path = current_path
        else:
            print(f"\t✅ MAIN_PATH loaded from .env: {main_path}")

        # 3. Ensure .env is listed in .gitignore
        if os.path.exists(gitignore_file):
            with open(gitignore_file, "r+") as f:
                lines = f.read().splitlines()
                if ".env" not in lines:
                    f.write("\n.env\n")
                    print("\t📝 Added .env to .gitignore.")
        else:
            with open(gitignore_file, "w") as f:
                f.write(".env\n")
                print("\t📝 Created .gitignore and added .env to it.")

        return main_path

    def _load_variables(self, yaml_path: str) -> Dict[str, str]:
        default_string = """User: 'your_user'""" # Aquí agregar las variables del YAML. 
        if not os.path.exists(yaml_path):
            with open(yaml_path, "w", encoding="utf-8") as pointer:
                pointer.write(default_string)
            print("Configuration file created at:")
            print(f"  {yaml_path}")
            print("Update it with your credentials before proceeding.")
            input("Press Enter after editing the file...")

        with open(yaml_path, "r", encoding="utf-8") as pointer:
            data_access = yaml.safe_load(pointer)

        default_keys = set(re.findall(r"^(\w+):", default_string, re.MULTILINE))
        yaml_keys = set(data_access.keys())
        extra_keys = yaml_keys - default_keys
        if extra_keys:
            print("Warning: new keys detected in config.yaml ->", ", ".join(extra_keys))
            print("Update the default template so future deployments remain consistent.")
        return data_access


if __name__ == "__main__":
    app = SQL_TO_LATEX()
    app.menu()
