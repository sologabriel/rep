{ pkgs }: {
  deps = [
    pkgs.vlc
    pkgs.libvlc
    pkgs.rtmpdump
    pkgs.inetutils
    pkgs.systemdMinimal
    pkgs.redis
    pkgs.bashInteractive
    pkgs.nodePackages.bash-language-server
    pkgs.man
  ];
  env = {
    PYTHON_LD_LIBRARY_PATH = pkgs.lib.makeLibraryPath [
      pkgs.rtmpdump
    ];
  };
}