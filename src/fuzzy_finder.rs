pub fn fuzzy_find(elements: Vec<String>, query: String) -> Vec<String> {
    if elements.is_empty() {
        return Vec::new();
    }
    let mut res: Vec<(usize, String)> = Vec::new();
    for el in elements {
        let count = does_match(&el.to_ascii_lowercase(), &query.to_ascii_lowercase());
        if let Some(count) = count {
            res.push((count, el));
        }
    }
    res.sort();
    return res.iter().map(|r| r.1.clone()).collect();
}

fn does_match(element: &str, query: &str) -> Option<usize> {
    let mut count = 0;
    let mut element = element;
    for c in query.chars() {
        let found = element.find(c);
        if let Some(index) = found {
            count += index;
            element = &element[(index + 1)..];
        } else {
            return None;
        }
    }
    return Some(count);
}

#[cfg(test)]
mod test_fuzzy_finder {
    use super::*;

    #[test]
    fn basic() {
        let res = fuzzy_find(
            vec![
                "var 2".to_string(),
                "var 3".to_string(),
                "v01".to_string(),
                "vAr 1".to_string(),
                "v1".to_string(),
            ],
            "v1".to_string(),
        );
        assert_eq!(
            res,
            vec!["v1".to_string(), "v01".to_string(), "vAr 1".to_string(),]
        );
    }
}
