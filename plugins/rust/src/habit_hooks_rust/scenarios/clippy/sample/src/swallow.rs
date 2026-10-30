pub fn touch(path: &str) {
    std::fs::remove_file(path);
}
