## linkage

Converts information about named entity and relation tags into pedigree [LINKAGE](https://www.mv.helsinki.fi/home/tsjuntun/autogscan/pedigreefile.html) file format and generates a pedigree plot. This implementation is specific for Norwegian and the annotations used for the [NorSynthClinical](https://github.com/ltgoslo/NorSynthClinical) corpus.
Entity and relation annotations are in the .uio files (e.g. from the 'pal_annotate' directory of NorSynthClinical). These can be used as input for this program to generate LINKAGE format (.ped) files and to plot pedigree charts (.png files) from those. Existing LINKAGE files can also be used as input directly to create plots. 
For plotting pedigree based on LINKAGE format, the kinship2 R package is used. For further information about the implementation, see the PDF.

This work was carried out as part of [BigMed](https://bigmed.no/) and it was discontinued after summer 2020 when my role in the project concluded. 

## Prerequisites

- R installed
- [kinship2](https://cran.r-project.org/web/packages/kinship2/index.html) installed

## Python dependencies

spacy_udpipe (with Norwegian Bokmål 'nb' model)

## Example runs

- `python to_linkage <input_file> <out_dir>`

### Single .uio file: generates a LINKAGE file (.ped) and a pedigree plot (.png)
- `python to_linkage to_linkage/examples/example1.uio to_linkage/examples`

### Single .ped file: generates a pedigree plot (.png)
- `python to_linkage to_linkage/examples/example1.ped to_linkage/examples`

## Terms of use

Distributed under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence.
