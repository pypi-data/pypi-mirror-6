import rtools

__all__ = ["install_all_cellnopt_dependencies"]


def install_all_cellnopt_dependencies(packages=None):
    """script to install all CellNOptR packages dependencies


    This is not complete but functional. So, we just need to add all relevant
    packages.

        >>> from cellnopt.admin import install_all_cellnopt_dependencies
        >>> install_all_cellnopt_dependencies()


    """
    pm = rtools.RPackageManager()
    installed_packages = pm.installed['Package']

    if packages == None:
        cellnopt = ["hash", "Rgraphviz", "RBGL", "graph", "RUnit", "igraph", "XML", "ggplot2", "RCurl"]
        ode= ["Rsolnp", "snowfall", "genalg"]
        feeder = ["catnet","minet"]
        meigor = ["Rsge"]
        fuzzy = ["xtable", "nloptr"]
        dt = []
        packages = cellnopt + meigor + fuzzy + feeder + ode + dt


    for package in packages:
        if package not in installed_packages:
            print("Installing %s " % package)
            rtools.biocLite(package)
        else:
            print("%s already installed. skipped" % package)

    # Rsge not maintained anymore so need to get it from arhive
    if "Rsge" not in installed_packages:
        pm.install_packages("http://cran.r-project.org/src/contrib/Archive/Rsge/Rsge_0.6.3.tar.gz")
    else:
        print("%s already installed. skipped" % "Rsge")

if __name__ == "__main__":
    install_all_cellnopt_dependencies()
