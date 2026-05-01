# FEK to Markdown Converter

CLI για μετατροπή ΦΕΚ σε PDF σε Markdown, με καθαρισμό ελληνικών line breaks και βασική δομή Markdown ώστε το περιεχόμενο να είναι πιο εύκολο να χρησιμοποιηθεί σε custom GPT knowledge base.

## Εγκατάσταση

```powershell
python -m venv .venv
.\.venv\Scripts\pip install -r requirements.txt
.\.venv\Scripts\pip install -e .
```

## Χρήση

Μετατροπή ενός PDF δίπλα στο αρχείο:

```powershell
.\.venv\Scripts\fek-to-md.exe path\to\fek.pdf
```

Με συγκεκριμένο output:

```powershell
.\.venv\Scripts\fek-to-md.exe path\to\fek.pdf -o output\fek.md
```

Μετατροπή όλων των PDF ενός φακέλου:

```powershell
.\.venv\Scripts\fek-to-md.exe input-folder -o output-folder
```

Αναδρομική αναζήτηση:

```powershell
.\.venv\Scripts\fek-to-md.exe input-folder -o output-folder --recursive
```

Χρήσιμες επιλογές:

```text
--overwrite        αντικαθιστά υπάρχοντα .md αρχεία
--no-page-markers  αφαιρεί τα <!-- Page N --> markers
--plain            κάνει μόνο καθαρισμό κειμένου, χωρίς Markdown headings
```

## Σημείωση για σκαναρισμένα ΦΕΚ

Το εργαλείο χρησιμοποιεί το επιλέξιμο κείμενο που υπάρχει μέσα στο PDF. Αν ένα ΦΕΚ είναι σκαναρισμένη εικόνα χωρίς OCR layer, θα εμφανιστεί warning για σελίδες με λίγο ή καθόλου κείμενο. Σε αυτή την περίπτωση χρειάζεται πρώτα OCR και μετά μετατροπή σε Markdown.
