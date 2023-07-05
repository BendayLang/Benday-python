#![allow(dead_code)]

mod ast;
mod fuzzy_finder;
mod math;
mod variables_expansion;

use ast_node::ReturnValue;
use math::MathParsability;
use pyo3::prelude::*;
use pyo3::types::PyFloat;

#[pyfunction]
fn fuzzy_find(possibilities: Vec<String>, query: String) -> PyResult<Vec<String>> {
    Ok(fuzzy_finder::fuzzy_find(possibilities, query))
}

#[pyfunction]
fn get_math_parsibility(expression: &str) -> PyResult<String> {
    match math::get_math_parsibility(expression) {
        MathParsability::IntParsable => Ok("int".to_string()),
        MathParsability::FloatParsable => Ok("float".to_string()),
        MathParsability::Unparsable => Ok("none".to_string()),
    }
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

// #[pyfunction]
// fn expand_variables(_expression: String, _variables: HashMap<String, &PyAny>) -> PyResult<String> {
//     //Ok(variables_expansion::expand_variables(expression, variables))
// }

/// A Python module implemented in Rust.
#[pymodule]
fn benday_rust(_py: Python, m: &PyModule) -> PyResult<()> {
    m.add_function(wrap_pyfunction!(math_expression, m)?)?;
    m.add_function(wrap_pyfunction!(get_math_parsibility, m)?)?;
    m.add_function(wrap_pyfunction!(fuzzy_find, m)?)?;
    // m.add_function(wrap_pyfunction!(expand_variables, m)?)?;
    Ok(())
}
