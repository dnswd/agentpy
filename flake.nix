{
  description = "A Nix-flake-based Python development environment";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/release-22.11";
    flake-utils.url = "github:numtide/flake-utils";
  };

  outputs =
    { self
    , nixpkgs
    , flake-utils
    , mach-nix
    }:

    flake-utils.lib.eachDefaultSystem (system:
    let
      overlays = [
        (self: super: rec {
          python = super.python310;
        })
      ];

      pkgs = import nixpkgs { inherit overlays system; };

      pythonEnv = (pkgs.poetry2nix.mkPoetryEnv {
        python = pkgs.python;
        projectDir = ./.;
        overrides = pkgs.poetry2nix.defaultPoetryOverrides.extend
          (self: super: {
            google-search-results = super.google-search-results.overridePythonAttrs
              (old: { buildInputs = (old.buildInputs) ++ [ super.setuptools ]; });
            beautifulsoup4 = super.beautifulsoup4.overridePythonAttrs
              (old: { buildInputs = (old.buildInputs) ++ [ super.hatchling ]; });
          });
      });
    in
    {
      devShells.default = pkgs.mkShell {
        nativeBuildInputs = (with pkgs; [ poetry ]) ++ [ pythonEnv ];

        shellHook = ''
          ${pythonEnv}/bin/python --version
        '';
      };
    });
}
