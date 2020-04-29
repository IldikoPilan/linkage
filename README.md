## linkage

Convert information about named entity and relation tags into LINKAGE format for pedigree visualization. This implementation is specific for Norwegian and the annotations used for the [NorSynthClinical](https://github.com/ltgoslo/NorSynthClinical) corpus.
Entity and relation annotations are in the .uio files. These can be used as input for this program to generate LINKAGE format (.ped) files and to plot pedigree charts (.png files) from those. Existing LINKAGE files can also be used as input directly to create plots. 
For plotting pedigree based on LINKAGE format, the kinship2 R package is used.

## Prerequisites

R installed
[kinship2](https://cran.r-project.org/web/packages/kinship2/index.html) installed

## Python dependencies

spacy_udpipe (with Norwegian Bokmål 'nb' model)

## Example run

### Single .uio file
python to_linkage /Users/ildikop/Documents/projects/UiO-BigMed/NorSynthClinical/pal_annotate/example1.uio to_linkage/examples

### Single .ped file
python to_linkage /Users/ildikop/Documents/projects/UiO-BigMed/NorSynthClinical/to_linkage/examples/example1.ped to_linkage/examples

## Terms of use