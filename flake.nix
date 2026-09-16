{
  description = "mikenrafter scout modules for contribution-graph art";

  inputs = {
    nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
    nix-scout.url = "github:mikenrafter/nix-scout";
    nix-scout.inputs.nixpkgs.follows = "nixpkgs";
  };

  outputs = { nixpkgs, nix-scout, ... }:
    let
      system = "x86_64-linux";
      packing = (import ./modules/graph-packing/flake.nix).outputs {
        inherit nixpkgs nix-scout;
      };
      snake = (import ./modules/graph-snake/flake.nix).outputs {
        inherit nixpkgs nix-scout;
      };
    in {
      packages.${system} = {
        graph-packing = packing.packages.${system}.graph-packing;
        graph-snake = snake.packages.${system}.graph-snake;
      };
      scoutModules = {
        graph-packing = ./modules/graph-packing;
        graph-snake = ./modules/graph-snake;
      };
      flakelets = {
        graph-packing = packing.flakelets.default;
        graph-snake = snake.flakelets.default;
      };
    };
}
