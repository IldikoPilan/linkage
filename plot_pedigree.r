#! /usr/local/bin/Rscript

library(kinship2)

plot_pedigree <- function(args) {
	p1 <- read.table(args[1], header=T) 	# indexing starts with 1				
	p2 <- as.data.frame(p1)				 	# transform to dataframe object
	attach(p2) 			 					# attach R object to search path				
	ped <- pedigree(id,fid,mid,sex,aff) 	# convert to pedigree obj	
	par(xpd = TRUE)	 						# set graph params
	png(file=args[2])					 	# get file name
	names <- strsplit(args[3], ",")[[1]] 	# need to index first element to get list
	id2 <- paste(ped$id, names, sep = "\n") # add family member names to IDs
	plot(ped,id=id2) 						# create plot
}

# Parse arguments
args = commandArgs(trailingOnly=TRUE)

plot_pedigree(args)