{
  description = "mikenrafter graph-packing contribution-art scout module";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  inputs.nix-scout.url = "github:mikenrafter/nix-scout";
  inputs.nix-scout.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { nixpkgs, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      graphPacking = pkgs.writeShellApplication {
        name = "graph-packing";
        runtimeInputs = [ pkgs.python3 ];
        text = ''
          export PYTHONPATH=${../..}
          exec ${pkgs.python3}/bin/python3 -m graph_art.cli "$@"
        '';
      };
    in
    pkgs.lib.optionalAttrs (inputs ? nix-scout) {
      packages = {
        ${system} = {
          default = graphPacking;
          graph-packing = graphPacking;
          scout = graphPacking;
        };
      };
      apps = {
        ${system}.graph-packing = {
          type = "app";
          program = "${graphPacking}/bin/graph-packing";
        };
      };
    } // {
      flakelets = {
        default =
        { types, ... }:
        {
          options = { };
          impl = { ... }: {
            exports.graphPacking = graphPacking;
          };
        };
      };
    };
}
