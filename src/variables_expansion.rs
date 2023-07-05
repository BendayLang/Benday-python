use ast_node::ReturnValue;
use std::collections::HashMap;

pub fn expand_variables(
    expression: &str,
    variables: &HashMap<String, ReturnValue>,
) -> Result<String, ()> {
    let start = expression.find('{');
    let end = expression.find('}');
    if start == None {
        if end == None {
            return Ok(expression.to_string());
        }
        return Err(());
    } else if end == None {
        return Err(()); // unclosed {
    }
    let start = start.unwrap();
    let end = end.unwrap();
    if start > end {
        return Err(());
    }
    let variable_name = &expression[start + 1..end];
    if !variables.contains_key(variable_name) {
        return Err(());
    }
    let result = expression[0..start].to_string()
        + &variables.get(variable_name).unwrap().to_string()
        + &expression[end + 1..];
    return expand_variables(&result, variables);
}

#[cfg(test)]
mod expand_variables_test {
    use super::*;
    #[test]
    fn basic() {
        let res = expand_variables(
            "salut {name}, votre nom c'est bien {name} n'est-ce pas ??",
            &HashMap::from(
                [(
                    "name".to_string(),
                    ReturnValue::String_("michelle".to_string()),
                ); 1],
            ),
        );
        assert_eq!(
            res,
            Ok("salut michelle, votre nom c'est bien michelle n'est-ce pas ??".to_string())
        );
    }

    #[test]
    fn age_de_bob() {
        assert_eq!(
            expand_variables(
                "{age de Bob} > 12",
                &HashMap::from([("age de Bob".to_string(), ReturnValue::Int(7)),])
            ),
            Ok("7 > 12".to_string())
        );
    }

    #[test]
    fn fail_unclosed() {
        assert_eq!(
            expand_variables("salut {unclosed   ", &HashMap::new()),
            Err(())
        );
        assert_eq!(
            expand_variables("salut }unclosed   ", &HashMap::new()),
            Err(())
        );
        assert_eq!(
            expand_variables("{salut unclosed   ", &HashMap::new()),
            Err(())
        );
        assert_eq!(
            expand_variables("}{salut unclosed   ", &HashMap::new()),
            Err(())
        );
    }
}
