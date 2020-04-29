## linkage

Convert information about named entity and relation tags into LINKAGE format for pedigree visualization. This implementation is specific for Norwegian and the annotations used for the [NorSynthClinical](https://github.com/ltgoslo/NorSynthClinical) corpus.
Entity and relation annotations are in the .uio files (e.g. from the pal_annotate/ directory of NorSynthClinical). These can be used as input for this program to generate LINKAGE format (.ped) files and to plot pedigree charts (.png files) from those. Existing LINKAGE files can also be used as input directly to create plots. 
For plotting pedigree based on LINKAGE format, the kinship2 R package is used.

## Prerequisites

R installed
[kinship2](https://cran.r-project.org/web/packages/kinship2/index.html) installed

## Python dependencies

spacy_udpipe (with Norwegian Bokmål 'nb' model)

## Example run

### Single .uio file
python to_linkage <path_to_uio_file> <out_dir>

### Single .ped file
python to_linkage <path_to_ped_file> <out_dir>

## Terms of use

Distributed under the [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/) licence.