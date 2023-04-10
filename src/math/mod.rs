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
