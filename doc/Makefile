all: projekt_rw.pdf

projekt_rw.pdf: projekt_rw.tex images/logo_agh.pdf
	texi2pdf -q -c $<

clean:
	rm -rf *.aux *.log *.out *.toc
