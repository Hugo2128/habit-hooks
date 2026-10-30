pub fn touch(path: &str) {
    let _ = std::fs::read_to_string(path);
}
