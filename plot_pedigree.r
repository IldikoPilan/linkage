#! /usr/local/bin/Rscript

library(kinship2)

plot_pedigree <- function(args) {
	pd <- read.table(args[1], header=T) 		# indexing starts with 1				
	pd_df <- as.data.frame(pd)					# transform to dataframe object
	print(pd_df)
	attach(pd_df) 			 					# attach R object to search path				
	ped <- pedigree(id,fid,mid,sex,aff) 		# convert to pedigree obj	
	options(device="png")
	par(xpd = TRUE)	 							# restrict plot to plotting region
	png(file=args[2])					 		# get file name
	if (length(args) == 3) {
  		names <- strsplit(args[3], ",")[[1]] 		# need to index first element to get list
		id2names <- paste(ped$id, names, sep = "\n")# add family member names to IDs
		plot(ped,id=id2names) 						# create plot with added names
	} else {
		plot(ped,id=ped$id) 						# create plot with original IDs
	}
	pdf(NULL)
}

# Parse arguments
args = commandArgs(trailingOnly=TRUE)
plot_pedigree(args)