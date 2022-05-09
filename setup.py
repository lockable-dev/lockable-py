import setuptools

with open("README.md", "r") as fh:
		long_description = fh.read()

setuptools.setup(
		name="lockable.dev",
		version="0.0.2",
		author="Lockable",
		author_email="dev@lockable.dev",
		description="Official Python client for https://lockable.dev",
		url="https://github.com/lockable-dev/lockable-py",
		long_description=long_description,
		long_description_content_type="text/markdown",
		packages=setuptools.find_packages(),
		classifiers=[
				"Programming Language :: Python :: 3",
				"License :: OSI Approved :: MIT License",
				"Operating System :: OS Independent",
		],
		python_requires='>=3.8',
		py_modules=["lockable"],
		package_dir={'':'src'},
		install_requires=[]
)
