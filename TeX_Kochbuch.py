import os
import re
import json

from Extend_Kochbuch import Kochbuch

OUT_PATH = "Kochbuch.tex"
PICTURES_PATH = "Bilder"

class KochbuchTex(Kochbuch):
    def __init__(self):
        super().__init__()

    def latex_escape(s: str) -> str:
        if not isinstance(s, str):
            s = str(s)
        
        # minimal escaping for common LaTeX special chars
        return re.sub(r'([#\$%&\~_\^\{\\\}])', r'\\\1', s)

    def normalize_list(field):
        if field is None:
            return []
        if isinstance(field, list):
            return [str(x) for x in field]
        if isinstance(field, str):
            # split by newlines or commas
            parts = [p.strip() for p in re.split(r'[\r\n]+|,', field) if p.strip()]
            return parts
        # fallback: try iterate
        try:
            return [str(x) for x in field]
        except Exception:
            return [str(field)]

    def generate_tex(self, out_path, prefix="Prefix.tex", postfix="Postfix.tex"):    
        with open(out_path, "w", encoding="utf-8") as f:
            # write prefix
            if prefix and os.path.isfile(prefix):
                with open(prefix, "r", encoding="utf-8") as pf:
                    f.write(pf.read() + "\n")

            # read existing chapters
            try:
                with open("Kapitel.json", "r", encoding="utf-8") as kap_file:
                    kapitel = json.load(kap_file)
            except Exception:
                kapitel = []

            # collect chapters from documents
            for doc in self.kochbuch["documents"]:
                kap = doc.get("Kapitel", "Lost and Found")
                if kap not in kapitel:
                    kapitel.append(kap)

            count = 0
            with open("Kapitel.json", "w", encoding="utf-8") as kap_file:
                json.dump(kapitel, kap_file, indent=4, ensure_ascii=False)

            # loop capturse
            for kap in kapitel:
                kap_title = kap
                print("Writing chapter: ", kap_title)
                kap_title_tex = KochbuchTex.latex_escape(kap_title)
                f.write(f"\\chapter{{{kap_title_tex}}}\n")

                for doc in self.kochbuch["documents"]:
                    if doc.get("Kapitel") != kap:
                        continue
                    count += 1
                    title = doc.get("Name","Unnamed")
                    print(f"Considering receipy {count}: ", title)
                    # common field names                
                    ingredients_field = doc.get("Zutaten", [])
                    instructions_field = doc.get("Anleitung", [])
                    notes = doc.get("Notes", "")
                    serves = doc.get("Serves", 1)
                    time = doc.get("Dauer", 10)

                    title_tex = KochbuchTex.latex_escape(title)
                    f.write(f"\\section{{{title_tex}}}\n")
                    f.write(f"\\index{{{title_tex}}}\n")

                    f.write("\\RecipeMeta{" + f"{serves}" + "}{" + f"{time}" + "}\n")

                    ingredients = KochbuchTex.normalize_list(ingredients_field)
                    if ingredients:
                        f.write("\\begin{ingredients}\n")
                        for ing in ingredients:
                            f.write(f"  \\item {KochbuchTex.latex_escape(ing)}\n")
                        f.write("\\end{ingredients}\n")


                    instructions = KochbuchTex.normalize_list(instructions_field)
                    if instructions:
                        f.write("\\begin{directions}\n")
                        for ing in instructions:
                            f.write(f"  \\item {KochbuchTex.latex_escape(ing)}\n")
                        f.write("\\end{directions}\n")

                    if doc.get("Bild"):
                        image_files = doc.get("Bild")
                        if isinstance(image_files, list) and len(image_files) > 0:
                            f.write("\\begin{figure}[h]\n")
                            f.write("\\centering\n")
                            for image_file in image_files:
                                file_path = f"{PICTURES_PATH}/{image_file}"
                                if os.path.isfile(file_path):
                                    f.write(f"\\includegraphics[height=0.5\\textheight]{{{KochbuchTex.latex_escape(file_path)}}}\n")
                            f.write(f"\\caption{{{title_tex}}}\n")
                            f.write("\\end{figure}\n")

                    if notes:
                        f.write("\\Notes{" + KochbuchTex.latex_escape(notes) + "}\n")

                    f.write("\\newpage\n")
            
            # write postfix
            if postfix and os.path.isfile(postfix):
                with open(postfix, "r", encoding="utf-8") as pf:
                    f.write(pf.read() + "\n")

def main():
    kochbuch = KochbuchTex()
    kochbuch.generate_tex(OUT_PATH)
    print(f"Wrote LaTeX to {OUT_PATH}")
    os.system(f"pdflatex -quiet {OUT_PATH}")
    os.system(f"makeindex Kochbuch.idx")
    os.system(f"pdflatex -quiet {OUT_PATH}")
    os.system("del *.aux *.log *.idx *.ind *.toc *.out *.ilg *.lof")
    os.system("move Kochbuch.pdf Output")
    os.system("move Kochbuch.tex Output")
    os.system("copy *.json Output")

if __name__ == "__main__":
    main()