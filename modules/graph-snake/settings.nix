{ ... }: {
  enable = true;
  output = "flakelets.default";
  settings = {
    repoPath = "/home/v0id/Documents/repos/mikenrafter";
    outputDir = "/home/v0id/Documents/repos/mikenrafter/output";
    githubUser = "mikenrafter";
    githubRepo = "mikenrafter/mikenrafter";
    user = "v0id";
    group = "users";
    home = "/home/v0id";
  };
}
