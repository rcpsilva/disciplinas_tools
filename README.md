# disciplinas_tools

Tools to convert JSON files with course information into `.tex` files for generating beautiful academic documents.

## About

This project provides Python scripts to automatically generate LaTeX files from JSON data. These scripts are designed to handle university course information, creating professional-looking documents that can be easily converted to PDF.

## Features

- **Automated LaTeX Generation**: Convert course data from JSON to `.tex` files effortlessly.
- **Two Conversion Modes**: Generate a separate `.tex` file for each course or a single `.tex` file for all courses.
- **Customizable Templates**: The LaTeX templates are embedded in the scripts and can be customized to fit different needs.
- **No External Dependencies**: The scripts are written in pure Python 3 and do not require any external libraries.

## Scripts

### `json2tex.py`

This script converts a single JSON object representing a course into a `.tex` file. The script takes a single argument: the path to the JSON file.

**Usage:**

```bash
python json2tex.py <path_to_json_file>
```

For example, if you have a file named `disciplina.json` with a single course, you can run:

```bash
python json2tex.py disciplina.json
```

This will generate a `disciplina.tex` file in the same directory.

### `json2tex2.py`

This script converts a list of courses from a JSON file into a single `.tex` file. It can also handle a JSON file with a single course object.

**Usage:**

```bash
python json2tex2.py <input_json_file> [output_tex_file]
```

- `<input_json_file>`: The path to the JSON file containing the course data.
- `[output_tex_file]`: (Optional) The path to the output `.tex` file. If not provided, the script will create a file with the same name as the input file, but with a `.tex` extension.

For example, to convert `disciplinas_bia.json` into `disciplinas_bia.tex`, you can run:

```bash
python json2tex2.py disciplinas_bia.json
```

To specify a different output file, you can run:

```bash
python json2tex2.py disciplinas_bia.json my_courses.tex
```

## JSON Format

The scripts expect a JSON file with a specific structure. For `json2tex2.py`, the JSON file should contain a single key "Disciplinas" with a list of course objects. For `json2tex.py`, the JSON file should contain a single course object.

Each course object should have the following keys:

- `Nome (ptBR)`: The name of the course in Portuguese.
- `Nome (enUS)`: The name of the course in English.
- `Código`: The course code.
- `Departamento`: The department responsible for the course.
- `Unidade Acadêmica`: The academic unit.
- `Modalidade`: The modality of the course (e.g., "presencial").
- `Carga Horária`: An object with the following keys:
  - `Total`: Total hours.
  - `Extensionista`: Extension hours.
  - `Teórica`: Theoretical hours.
  - `Prática`: Practical hours.
- `Ementa`: The course syllabus.
- `Conteúdo Programático`: A list of strings with the programmatic content.
- `Bibliografia Básica`: A list of strings with the basic bibliography.
- `Bibliografia Complementar`: A list of strings with the complementary bibliography.

Here is an example of a single course object:

```json
{
  "Nome (ptBR)": "Programação Orientada a Objetos",
  "Nome (enUS)": "Object Oriented Programming",
  "Código": "BCC138",
  "Departamento": "Departamento de Computação (DECOM)",
  "Unidade Acadêmica": "ICEB",
  "Modalidade": "presencial",
  "Carga Horária": {
    "Total": "60",
    "Extensionista": "0",
    "Teórica": "4",
    "Prática": "0"
  },
  "Ementa": "Conceitos básicos de orientação a objetos...",
  "Conteúdo Programático": [
    "Visão geral do paradigma de programação orientada a objetos",
    "Modelagem UML",
    "Classes, objetos, mensagens"
  ],
  "Bibliografia Básica": [
    "DEITEL, Harvey M.; DEITEL, P. J. C++ como programar. 5. ed. São Paulo: Pearson Prentice Hall, 2006."
  ],
  "Bibliografia Complementar": [
    "LEE, Richard C.; TEPFENHART, William M. UML e C++: guia prático de desenvolvimento orientado a objeto. Pearson, 2001."
  ]
}
```

## Dependencies

The scripts are written in Python 3 and do not require any external libraries. You just need to have a Python 3 interpreter installed on your system.

## Generating the PDF

After generating the `.tex` file, you can compile it to a PDF using a LaTeX distribution like TeX Live, MiKTeX, or MacTeX. The following command uses `pdflatex` to generate the PDF:

```bash
pdflatex <your_tex_file>.tex
```

For example, to generate a PDF from `disciplina.tex`, you would run:

```bash
pdflatex disciplina.tex
```

Note that you may need to run the command twice to ensure that all references are correctly generated. Also, the LaTeX templates use the `brasao.png` and `ufop.png` images, so make sure they are in the same directory as the `.tex` file, or provide the correct path in the template.
