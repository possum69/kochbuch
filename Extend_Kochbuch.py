import os
import json

try:
    import pytesseract
except ImportError:
    print("pytesseract not found, OCR functionality will be disabled.")
    pytesseract = None

IMAGES_FOLDER = "Quellen"
LOST_AND_FOUND = "Lost and Found"
NAME = "Name"
ANLEITUNG = "Anleitung"
ZUTATEN = "Zutaten"
NOTES = "Notes"

class Kochbuch():
    def __init__(self):
        with open("Kochbuch.json", "r", encoding="utf-8") as f:
            self.kochbuch = json.load(f)
        self.known_names = [doc[NAME] for doc in self.kochbuch["documents"]]

    def upload_documents(self, documents):
        for doc in documents:
            name = doc.get(NAME,"Unnamed")
            if name in self.known_names:
                print("Existing document found!", name)
                continue
            print("Uploading receipy: ", name)
            if doc.get("Kapitel") is None:  
                doc["Kapitel"] = LOST_AND_FOUND
            if doc.get("Serves") is None:  
                doc["Serves"] = 1

            self.kochbuch["documents"].append(doc)
            print("Uploaded document: ", doc[NAME])
            self.known_names.append(name)

    # === OCR Function ===
    def extract_text_from_image(self, image_path):
        try:
            img = Image.open(image_path)
            text = pytesseract.image_to_string(img, lang="deu")  # change 'deu' to 'eng' or another language if needed
            return text.strip()
        except Exception as e:
            print(f"⚠️ OCR failed for {image_path}: {e}")
            return ""
        
    # === Function to upload image and link to document ===
    def upload_image_and_link(self, image_path, name):
        image_name = os.path.basename(image_path)

        # Link file ID to the document in the database
        #notes = self.extract_text_from_image(image_path)
        notes = ""
        print(f"Create document with image for {name}...", notes)
        
        self.kochbuch["documents"].append({
                "Bild": image_name,
                "Name": name,
                "Notes": None,
                "Serves": 1,
                "Kapitel": LOST_AND_FOUND
                }
        )
        print(f"✅ Linked {image_name} to document {name}")

def main():
    kochbuch = Kochbuch()
    print("Starting Uploader")
    receipies = []
    directory = "Input"
    files = json_files = [f for f in os.listdir(directory) if f.endswith(".json")]
    print("found files: ", files)
    for f in files:
        print("reading ", f)
        inputfile = os.path.join("Input", f)
        with open(inputfile, "r", encoding="utf-8") as f:
            try:
                input = json.load(f)
                if isinstance(input, dict):
                    input = [input]
                for rec in input:
                    print("adding recepie: ", rec.get(NAME, "Unnamed"))
                    receipies.append(rec)
            except json.JSONDecodeError as e:
                print(f"❌ Failed to parse {inputfile}: {e}")

    kochbuch.upload_documents(receipies)

    for filename in os.listdir(IMAGES_FOLDER):
        name = ".".join(filename.split('.')[0:-1])
        if name in kochbuch.known_names:
            print("Image for known document found, skipping upload: ", filename)
            continue
        if filename.lower().endswith(".jpg"):
            file_path = os.path.join(IMAGES_FOLDER, filename)

            try:
                kochbuch.upload_image_and_link(file_path, name)
                kochbuch.known_names.append(name)
            except Exception as e:
                print(f"❌ Failed to upload {filename}: {e}")

    with open("Kochbuch.json", "w", encoding="utf-8") as f:
        total = len(kochbuch.kochbuch["documents"])
        kochbuch.kochbuch["total"] = total
        json.dump(kochbuch.kochbuch, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    main()
    