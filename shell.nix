# https://search.nixos.org/packages
# https://www.boronine.com/2018/02/02/Nix/
with import <nixpkgs> {};
let
	pythonEnv = python310.withPackages (ps: with ps; [
		numpy
		astropy
		# use `sys.path.append('/usr/lib/python3.10/site-packages')` for now
#		astroquery	# FIXME doesn't compile
		matplotlib
		pip
	]);
in mkShell {
	packages = [
		pythonEnv
		tup
		imagemagick
		ffmpeg
	];
#	shellHook = ''
#		pip install astroquery
#	'';
}
