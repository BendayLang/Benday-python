mod ast;
mod fuzzy_finder;
mod math;
mod variables_expansion;

#[allow(unused_imports)]
use ast::{exec_ast, ASTNode, ReturnValue};
use pyo3::prelude::*;
use pyo3::types::PyFloat;
use std::collections::HashMap;

/*
#[pyfunction]
fn execute_ast(_ast: Vec<String>, _query: String) -> PyResult<()> {
    let ast = ASTNode::Sequence(Vec::new());
    let mut variables = HashMap::new();
    exec_ast(&ast, &mut variables);
    Ok(())
}
*/

#[pyfunction]
fn fuzzy_find(possibilities: Vec<String>, query: String) -> PyResult<Vec<String>> {
    Ok(fuzzy_finder::fuzzy_find(possibilities, query))
}

#[pyfunction]
fn is_math_parsable(expression: &str) -> PyResult<bool> {
    Ok(math::is_math_parsable(expression))
}

#[pyfunction]
fn math_expression(expression: &str) -> PyResult<f64> {
    match math::math_expression(expression) {
        Ok(ReturnValue::Float(value)) => Ok(value),
        Ok(ReturnValue::Int(value)) => Ok(value as f64),
        Ok(ReturnValue::Bool(value)) => Ok(if value { 1.0 } else { 0.0 }),
        Ok(ReturnValue::None) => Err(PyErr::new::<PyFloat, _>("Math expression failed (None)")),
        Ok(ReturnValue::String_(_)) => {
            Err(PyErr::new::<PyFloat, _>("Math expression failed (String)"))
        }
        _ => Err(PyErr::new::<PyFloat, _>("Math expression failed (Unknown)")),
    }
}

#[pyfunction]
fn expand_variables(_expression: String, _variables: HashMap<String, &PyAny>) -> PyResult<String> {
    //Ok(variables_expansion::expand_variables(expression, variables))
    Ok(String::from("todo"))
}

/// A Python module implemented in Rust.
#[pymodule]
fn benday_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(math_expression, m)?)?;
    m.add_function(wrap_pyfunction!(is_math_parsable, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_find, m)?)?;
    m.add_function(wrap_pyfunction!(expand_variables, m)?)?;
    Ok(())
}
