{
  description = "Tamboerijn, music tagged my way";

  inputs = {
    nixpkgs.url = "github:nixos/nixpkgs/nixos-23.11";
    flake-utils.url = "github:numtide/flake-utils";
    pre-commit-hooks.url = "github:cachix/pre-commit-hooks.nix";
  };

  outputs = { self, nixpkgs, flake-utils, pre-commit-hooks }:
    flake-utils.lib.eachSystem [ flake-utils.lib.system.x86_64-linux ] (system:
      let
        pkgs = nixpkgs.legacyPackages.${system};
        my-python-packages = ps: with ps; [
          mutagen # handling audio tags
          tqdm # parrallel progress bar
          (
            buildPythonPackage rec {
              pname = "p_tqdm";
              version = "1.4.0";
              src = fetchPypi {
                inherit pname version;
                sha256 = "sha256-DRKqIjRD84ckTM5edKCuzEctH5gYnVjM382oZ3J3K/w=";
              };
              doCheck = false;
              propagatedBuildInputs = [
                pathos
              ];
            }
          )
        ];
      in
      {
        devShells.default = pkgs.mkShell {
          buildInputs = with pkgs; [
            (python3.withPackages my-python-packages)
            gtk4
          ];
        };

        checks = {
          pre-commit-check = pre-commit-hooks.lib.${system}.run {
            src = ./.;
            hooks = {
              nixpkgs-fmt.enable = true;
              pylint.enable = true;
            };
          };
          # app = self.packages.${system}.default;
        };

        # packages.default = TODO
      }
    );
}
