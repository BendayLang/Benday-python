use crate::math::math_parser::MathNode;
use crate::math::math_parser::Operation;
use ast_node::ReturnValue;
/*
pub enum MathNode {
    Operation(Box<MathNode>, Operation, Box<MathNode>),
    Float(f64),
    Int(isize),
}
*/

pub fn execute_ast(ast: MathNode) -> Result<ReturnValue, ()> {
    match ast {
        MathNode::Operation(l, op, r) => match op {
            Operation::Addition => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Int(l + r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l + r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l as f64 + r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Float(l + r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Substraction => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Int(l - r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l - r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l as f64 - r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Float(l - r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Multiplication => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Int(l * r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l * r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l as f64 * r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Float(l * r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Division => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Int(l / r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l / r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l as f64 / r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Float(l / r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Modulo => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Int(l % r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l % r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l as f64 % r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Float(l % r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Power => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Int(l.pow(r as u32)));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float(l.powf(r)));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Float((l as f64).powf(r)));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Float(l.powf(r as f64)));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::And => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l != 0 && r != 0));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l != 0.0 && r != 0.0));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l != 0 && r != 0.0));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l != 0.0 && r != 0));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Or => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l != 0 || r != 0));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l != 0.0 || r != 0.0));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l != 0 || r != 0.0));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l != 0.0 || r != 0));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Lesser => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l < r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l < r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool((l as f64) < r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l < r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::Greater => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l > r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l > r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool((l as f64) > r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l > r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::EqGreater => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l >= r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l >= r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool((l as f64) >= r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l >= r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            Operation::EqLesser => {
                let l = execute_ast(*l)?;
                let r = execute_ast(*r)?;
                match (l, r) {
                    (ReturnValue::Int(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l <= r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool(l <= r));
                    }
                    (ReturnValue::Int(l), ReturnValue::Float(r)) => {
                        return Ok(ReturnValue::Bool((l as f64) <= r));
                    }
                    (ReturnValue::Float(l), ReturnValue::Int(r)) => {
                        return Ok(ReturnValue::Bool(l <= r as f64));
                    }
                    _ => {
                        return Err(());
                    }
                }
            }
            _ => {
                todo!("executor for {:?}", op);
            }
        },
        MathNode::Float(f) => {
            return Ok(ReturnValue::Float(f));
        }
        MathNode::Int(i) => {
            return Ok(ReturnValue::Int(i));
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_execute_ast() {
        let ast = MathNode::Operation(
            Box::new(MathNode::Int(1)),
            Operation::Addition,
            Box::new(MathNode::Int(2)),
        );
        assert_eq!(execute_ast(ast).unwrap(), ReturnValue::Int(3));
    }

    #[test]
    fn test_execute_ast_float() {
        let ast = MathNode::Operation(
            Box::new(MathNode::Float(1.0)),
            Operation::Addition,
            Box::new(MathNode::Float(2.0)),
        );
        assert_eq!(execute_ast(ast).unwrap(), ReturnValue::Float(3.0));
    }

    #[test]
    fn test_execute_ast_float_int() {
        let ast = MathNode::Operation(
            Box::new(MathNode::Float(1.0)),
            Operation::Addition,
            Box::new(MathNode::Int(2)),
        );
        assert_eq!(execute_ast(ast).unwrap(), ReturnValue::Float(3.0));
    }

    #[test]
    fn test_execute_ast_int_float() {
        let ast = MathNode::Operation(
            Box::new(MathNode::Int(1)),
            Operation::Addition,
            Box::new(MathNode::Float(2.0)),
        );
        assert_eq!(execute_ast(ast).unwrap(), ReturnValue::Float(3.0));
    }

    #[test]
    fn test_execute_ast_bool() {
        let ast = MathNode::Operation(
            Box::new(MathNode::Int(1)),
            Operation::And,
            Box::new(MathNode::Int(2)),
        );
        assert_eq!(execute_ast(ast).unwrap(), ReturnValue::Bool(true));
    }

    #[test]
    fn test_execute_ast_bool_float() {
        let ast = MathNode::Operation(
            Box::new(MathNode::Float(1.0)),
            Operation::And,
            Box::new(MathNode::Float(0.0)),
        );
        assert_eq!(execute_ast(ast).unwrap(), ReturnValue::Bool(false));
    }
}
