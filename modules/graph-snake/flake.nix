{
  description = "mikenrafter GitHub contribution snake scout module";

  inputs.nixpkgs.url = "github:NixOS/nixpkgs/nixos-26.05";
  inputs.nix-scout.url = "github:mikenrafter/nix-scout";
  inputs.nix-scout.inputs.nixpkgs.follows = "nixpkgs";

  outputs = { nixpkgs, ... }@inputs:
    let
      system = "x86_64-linux";
      pkgs = import nixpkgs { inherit system; };
      lib = pkgs.lib;
      snakeGenerator = pkgs.writeShellApplication {
        name = "graph-snake";
        runtimeInputs = [ pkgs.podman ];
        text = ''
          : "''${INPUT_GITHUB_USER_NAME:?set INPUT_GITHUB_USER_NAME}"
          : "''${INPUT_GITHUB_TOKEN:?set INPUT_GITHUB_TOKEN}"
          : "''${INPUT_OUTPUTS:?set INPUT_OUTPUTS}"
          exec podman run --rm --userns=keep-id \
            --volume "''${PWD}:''${PWD}:Z" --workdir "''${PWD}" \
            --env "INPUT_GITHUB_USER_NAME=''${INPUT_GITHUB_USER_NAME}" \
            --env "INPUT_GITHUB_TOKEN=''${INPUT_GITHUB_TOKEN}" \
            --env "INPUT_OUTPUTS=''${INPUT_OUTPUTS}" \
            docker.io/platane/snk@sha256:3a66a51ca8eaecc1e841bc8baae39bd88079e57419850d1ed005eee2bbfce940
        '';
      };
    in
    pkgs.lib.optionalAttrs (inputs ? nix-scout) {
      packages = {
        ${system} = {
          default = snakeGenerator;
          graph-snake = snakeGenerator;
          generator = snakeGenerator;
          scout = snakeGenerator;
        };
      };
    } // {
      flakelets = {
        default =
        { types, ... }:
        {
          options = {
            repoPath = { type = types.string; default = "/home/v0id/Documents/repos/mikenrafter"; description = "Profile repository clone."; };
            outputDir = { type = types.string; default = "/home/v0id/Documents/repos/mikenrafter/output"; description = "Generated SVG directory."; };
            githubUser = { type = types.string; default = "mikenrafter"; description = "GitHub username."; };
            githubRepo = { type = types.string; default = "mikenrafter/mikenrafter"; description = "GitHub repository."; };
            user = { type = types.string; default = "v0id"; description = "Service user."; };
            group = { type = types.string; default = "users"; description = "Service group."; };
            home = { type = types.string; default = "/home/v0id"; description = "Service HOME."; };
          };

          impl = { options, pkgs, name, ... }:
            let
              repoPath = options.repoPath;
              outputDir = options.outputDir;
              lightSvg = "${outputDir}/github-contribution-grid-snake.svg";
              darkSvg = "${outputDir}/github-contribution-grid-snake-dark.svg";
              git = "${pkgs.git}/bin/git";
              gh = "${pkgs.gh}/bin/gh";
              realpath = "${pkgs.coreutils}/bin/realpath";
              startScript = pkgs.writeShellScript "graph-snake-generate" ''
                set -euo pipefail
                if ! ${gh} auth status --hostname github.com >/dev/null 2>&1; then
                  echo "graph-snake: authenticate first with 'gh auth login'." >&2
                  exit 1
                fi
                cd ${lib.escapeShellArg repoPath}
                branch="$(${git} branch --show-current)"
                if [ "$branch" != "main" ]; then
                  echo "graph-snake: invariant violated: expected branch main, got ''${branch}" >&2
                  exit 1
                fi
                ${git} fetch --quiet origin main
                ahead_before="$(${git} rev-list --count origin/main..HEAD)"
                if [ "$ahead_before" -ne 0 ]; then
                  echo "graph-snake: invariant violated: expected zero unpushed commits on main before snake commit, found ''${ahead_before}" >&2
                  exit 1
                fi
                ${git} merge --ff-only --quiet origin/main
                ${pkgs.coreutils}/bin/mkdir -p ${lib.escapeShellArg outputDir}
                token="$(${gh} auth token --hostname github.com)"
                ${pkgs.podman}/bin/podman run --rm --userns=keep-id \
                  --volume ${lib.escapeShellArg "${repoPath}:${repoPath}:Z"} \
                  --workdir ${lib.escapeShellArg repoPath} \
                  --env "INPUT_GITHUB_USER_NAME=${options.githubUser}" \
                  --env "INPUT_GITHUB_TOKEN=$token" \
                  --env "INPUT_OUTPUTS=${lightSvg}
                ${darkSvg}?palette=github-dark" \
                  docker.io/platane/snk@sha256:3a66a51ca8eaecc1e841bc8baae39bd88079e57419850d1ed005eee2bbfce940
                rel_light="$(${realpath} --relative-to=${lib.escapeShellArg repoPath} ${lib.escapeShellArg lightSvg})"
                rel_dark="$(${realpath} --relative-to=${lib.escapeShellArg repoPath} ${lib.escapeShellArg darkSvg})"
                ${git} add -- "$rel_light" "$rel_dark"
                if ${git} diff --quiet --cached -- "$rel_light" "$rel_dark"; then
                  echo "graph-snake: SVGs unchanged; skipping commit and push."
                  exit 0
                fi
                while IFS= read -r path; do
                  if [ "$path" != "$rel_light" ] && [ "$path" != "$rel_dark" ]; then
                    echo "graph-snake: invariant violated: staged unexpected path: ''${path}" >&2
                    exit 1
                  fi
                done < <(${git} diff --cached --name-only)
                ${git} -c user.name=graph-snake -c user.email=graph-snake@users.noreply.github.com \
                  commit --quiet -m "chore: refresh contribution snake" -- "$rel_light" "$rel_dark"
                while IFS= read -r path; do
                  if [ "$path" != "$rel_light" ] && [ "$path" != "$rel_dark" ]; then
                    echo "graph-snake: invariant violated: commit includes unexpected path: ''${path}" >&2
                    exit 1
                  fi
                done < <(${git} diff-tree --no-commit-id --name-only -r HEAD)
                branch="$(${git} branch --show-current)"
                if [ "$branch" != "main" ]; then
                  echo "graph-snake: invariant violated: expected branch main at push time, got ''${branch}" >&2
                  exit 1
                fi
                ahead="$(${git} rev-list --count origin/main..HEAD)"
                if [ "$ahead" -ne 1 ]; then
                  echo "graph-snake: invariant violated: expected exactly one commit to push, found ''${ahead}" >&2
                  exit 1
                fi
                push_url="https://x-access-token:''${token}@github.com/${options.githubRepo}.git"
                for attempt in 1 2 3; do
                  if ${git} push --quiet "$push_url" HEAD:main; then
                    echo "graph-snake: pushed one commit on main with only snake SVG changes."
                    exit 0
                  fi
                  if [ "$attempt" -eq 3 ]; then
                    echo "graph-snake: push failed after three attempts." >&2
                    exit 1
                  fi
                  echo "graph-snake: main moved during push, rebasing generated commit and retrying (attempt $((attempt + 1))/3)." >&2
                  ${git} fetch --quiet origin main
                  ahead_after_fetch="$(${git} rev-list --count origin/main..HEAD)"
                  if [ "$ahead_after_fetch" -ne 1 ]; then
                    echo "graph-snake: invariant violated: expected exactly one generated commit after refetch, found ''${ahead_after_fetch}" >&2
                    exit 1
                  fi
                  ${git} rebase --quiet origin/main
                  while IFS= read -r path; do
                    if [ "$path" != "$rel_light" ] && [ "$path" != "$rel_dark" ]; then
                      echo "graph-snake: invariant violated: rebased commit includes unexpected path: ''${path}" >&2
                      exit 1
                    fi
                  done < <(${git} diff-tree --no-commit-id --name-only -r HEAD)
                done
              '';
            in {
              exports.generator = snakeGenerator;
              services.${name} = {
                description = "Generate and publish GitHub profile contribution snake";
                after = [ "network-online.target" ];
                wants = [ "network-online.target" ];
                serviceConfig = {
                  Type = "oneshot";
                  User = options.user;
                  Group = options.group;
                  ExecStart = startScript;
                  WorkingDirectory = repoPath;
                  Environment = [ "HOME=${options.home}" "XDG_CONFIG_HOME=${options.home}/.config" ];
                };
              };
              timers.${name} = {
                description = "Refresh GitHub profile contribution snake daily";
                wantedBy = [ "timers.target" ];
                timerConfig = { OnCalendar = "daily"; Persistent = true; Unit = "${name}.service"; };
              };
            };
        };
      };
    };
}
