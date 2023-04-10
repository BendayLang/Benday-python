mod ast;
mod fuzzy_finder;
mod math;
mod variables_expansion;
use ast::{exec_ast, ASTNode};
use pyo3::prelude::*;
use std::collections::HashMap;

#[pyfunction]
fn execute_ast(ast: Vec<String>, query: String) -> PyResult<()> {
    let ast = ASTNode::Sequence(Vec::new());
    let mut variables = HashMap::new();
    exec_ast(&ast, &mut variables);
    Ok(())
}

#[pyfunction]
fn fuzzy_find(possibilities: Vec<String>, query: String) -> PyResult<Vec<String>> {
    Ok(fuzzy_finder::fuzzy_find(possibilities, query))
}

#[pyfunction]
fn expand_variables(expression: String, variables: HashMap<String, &PyAny>) -> PyResult<String> {
    //Ok(variables_expansion::expand_variables(expression, variables))
    Ok(String::from("todo"))
}

/// A Python module implemented in Rust.
#[pymodule]
fn benday_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(execute_ast, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_find, m)?)?;
    m.add_function(wrap_pyfunction!(expand_variables, m)?)?;
    Ok(())
}
