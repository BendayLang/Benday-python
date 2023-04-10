mod executor;
mod math_parser;
mod tokenizer;
use crate::ast::ReturnValue;
use executor::execute_ast;
use math_parser::parse_math_expression;
use tokenizer::tokenize_expression;

pub fn is_math_parsable(expression: &str) -> bool {
    match tokenize_expression(&expression) {
        Ok(_) => true,
        Err(_) => false,
    }
}

pub fn math_expression(expression: &str) -> Result<ReturnValue, ()> {
    let tokens = match tokenize_expression(expression) {
        Ok(v) => v,
        Err(_) => return Err(()),
    };
    let ast = parse_math_expression(tokens)?;
    execute_ast(ast)
}

#[cfg(test)]
mod integration_tests {
    use super::*;

    #[test]
    fn simple_addition() {
        assert_eq!(math_expression("1 + 1"), Ok(ReturnValue::Int(2)));
    }

    #[test]
    fn stick_simple_addition() {
        assert_eq!(math_expression("1+1"), Ok(ReturnValue::Int(2)));
    }

    #[test]
    fn simple_substraction() {
        assert_eq!(math_expression("1 - 1"), Ok(ReturnValue::Int(0)));
    }

    #[test]
    fn simple_multiplication() {
        assert_eq!(math_expression("2 * 2"), Ok(ReturnValue::Int(4)));
    }

    #[test]
    fn simple_division() {
        assert_eq!(math_expression("2 / 2"), Ok(ReturnValue::Int(1)));
    }

    #[test]
    fn simple_modulo() {
        assert_eq!(math_expression("2 % 2"), Ok(ReturnValue::Int(0)));
    }

    #[test]
    fn simple_power() {
        assert_eq!(math_expression("2 ^ 2"), Ok(ReturnValue::Int(4)));
    }

    #[test]
    fn simple_parenthesis() {
        assert_eq!(math_expression("(2+2)"), Ok(ReturnValue::Int(4)));
    }

    #[test]
    fn simple_parenthesis_with_spaces() {
        assert_eq!(math_expression("( 2 + 2 )"), Ok(ReturnValue::Int(4)));
    }

    #[test]
    fn simple_parenthesis_with_spaces_and_operations() {
        assert_eq!(math_expression("( 2 + 2 ) * 2"), Ok(ReturnValue::Int(8)));
    }
}
