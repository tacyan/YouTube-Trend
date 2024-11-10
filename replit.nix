{pkgs}: {
  deps = [
    pkgs.chromedriver
    pkgs.chromium
    pkgs.geckodriver
    pkgs.postgresql
    pkgs.openssl
  ];
}
