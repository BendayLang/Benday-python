use crate::math;
use crate::variables_expansion::expand_variables;
use std::collections::HashMap;
use std::fmt;

mod user_prefs {
    pub const MAX_ITERATION: usize = 100;
}

pub fn exec_ast(ast: &ASTNode, variables: &mut HashMap<String, ReturnValue>) -> ReturnValue {
    match ast {
        ASTNode::Sequence(sequence) => {
            for instruction in sequence {
                let return_value: ReturnValue = exec_ast(instruction, variables);
                if return_value != ReturnValue::None {
                    return return_value;
                }
            }
            return ReturnValue::None;
        }
        ASTNode::While(is_do, condition, sequence) => {
            if *is_do {
                let return_value = exec_ast(&ASTNode::Sequence(sequence.clone()), variables);
                if return_value != ReturnValue::None {
                    return return_value;
                }
            }
            let mut iteration = 0;
            while iteration != user_prefs::MAX_ITERATION && get_bool(exec_ast(condition, variables))
            {
                let return_value = exec_ast(&ASTNode::Sequence(sequence.clone()), variables);
                if return_value != ReturnValue::None {
                    return return_value;
                }
                iteration += 1;
            }
            if iteration == user_prefs::MAX_ITERATION {
                todo!("break on max iteration ({})", user_prefs::MAX_ITERATION);
            }
            return ReturnValue::None;
        }
        ASTNode::IfElse(ifelse) => {
            if get_bool(exec_ast(&ifelse.if_.condition, variables)) {
                let _return_value =
                    exec_ast(&ASTNode::Sequence(ifelse.if_.sequence.clone()), variables);
            }
            if let Some(elifs) = &ifelse.elif {
                for elif in elifs {
                    if get_bool(exec_ast(&elif.condition, variables)) {
                        let _return_value =
                            exec_ast(&ASTNode::Sequence(elif.sequence.clone()), variables);
                    }
                }
            }
            if let Some(else_) = &ifelse.else_ {
                if get_bool(exec_ast(&else_.condition, variables)) {
                    let _return_value =
                        exec_ast(&ASTNode::Sequence(else_.sequence.clone()), variables);
                }
            }
            return ReturnValue::None;
        }
        ASTNode::Value(value) => {
            let value: String = if let Some(_) = value.find("{") {
                match expand_variables(&value, variables) {
                    Ok(v) => v.to_string(),
                    Err(()) => todo!("erreur expand_variables, comment reagir ?"),
                }
            } else {
                value.to_string()
            };
            return match math::get_math_parsibility(&value) {
                math::MathParsability::Unparsable => ReturnValue::String_(value),
                math::MathParsability::FloatParsable => math::math_expression(&value).unwrap(),
                math::MathParsability::IntParsable => math::math_expression(&value).unwrap(),
            };
        }
        ASTNode::VariableAssignment(name, new_value) => {
            let value = exec_ast(new_value, variables);
            if variables.contains_key(name) {
                variables.remove(name);
            }
            variables.insert(name.to_string(), value);
            return ReturnValue::None;
        }
        ASTNode::FunctionCall(function) => {
            if function.is_builtin && function.name == "print" {
                for inst in &function.argv {
                    println!("{:?}", exec_ast(&inst, variables));
                }
                return ReturnValue::None;
            }
            return ReturnValue::None;
        }
    }
}

fn get_bool(return_value: ReturnValue) -> bool {
    match return_value {
        ReturnValue::Bool(val) => val,
        ReturnValue::None => false,
        ReturnValue::String_(val) => todo!("error should return a bool, not a string ({val})"),
        ReturnValue::Int(val) => val != 0,
        ReturnValue::Float(val) => val != 0.0,
    }
}

#[allow(dead_code)]
#[derive(Debug, Clone)]
pub enum ASTNode {
    Sequence(Vec<ASTNode>),
    While(bool, Box<ASTNode>, Vec<ASTNode>),
    IfElse(IfElse),
    Value(String),
    VariableAssignment(String, Box<ASTNode>),
    FunctionCall(Function),
}

#[derive(Debug, PartialEq, Clone)]
pub enum ReturnValue {
    String_(String),
    Int(isize),
    Float(f64),
    Bool(bool),
    None,
}

impl fmt::Display for ReturnValue {
    fn fmt(&self, f: &mut fmt::Formatter<'_>) -> fmt::Result {
        match self {
            ReturnValue::String_(str) => write!(f, "{str}"),
            ReturnValue::Int(val) => write!(f, "{val}"),
            ReturnValue::Float(val) => write!(f, "{val}"),
            ReturnValue::Bool(val) => write!(f, "{val}"),
            ReturnValue::None => write!(f, "None"),
        }
    }
}

#[derive(Debug, Clone)]
pub struct If {
    pub condition: Box<ASTNode>,
    pub sequence: Vec<ASTNode>,
}

#[derive(Debug, Clone)]
pub struct IfElse {
    pub if_: If,
    pub elif: Option<Vec<If>>,
    pub else_: Option<If>,
}

#[derive(Debug, Clone)]
pub struct Function {
    pub name: String,
    pub is_builtin: bool,
    pub argv: Vec<ASTNode>,
}

/* ********************** */

#[cfg(test)]
mod test {
    use super::*;
    #[test]
    fn ast_executor_test() {
        let ast = ASTNode::Sequence(vec![
            ASTNode::VariableAssignment(
                "age de Bob".to_string(),
                Box::new(ASTNode::Value("6".to_string())),
            ),
            ASTNode::While(
                false,
                Box::new(ASTNode::Value("{age de Bob} < 13".to_string())),
                vec![
                    ASTNode::VariableAssignment(
                        "age de Bob".to_string(),
                        Box::new(ASTNode::Value("{age de Bob} + 1".to_string())),
                    ),
                    ASTNode::FunctionCall(Function {
                        name: "print".to_string(),
                        is_builtin: true,
                        argv: vec![ASTNode::Value(
                            "Bravo Bob ! tu as maintenant {age de Bob} ans !".to_string(),
                        )],
                    }),
                ],
            ),
            ASTNode::FunctionCall(Function {
                name: "print".to_string(),
                is_builtin: true,
                argv: vec![ASTNode::Value(
                    "Bob est parti a l'age de {age de Bob} !".to_string(),
                )],
            }),
        ]);
        let mut variables: HashMap<String, ReturnValue> = HashMap::new();
        exec_ast(&ast, &mut variables);
    }
}
