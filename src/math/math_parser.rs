use crate::ast::ReturnValue;
use crate::math::tokenizer::{tokenize_expression, Token};

#[derive(Debug, PartialEq, Clone)]
pub enum Operation {
    // A
    OpenParenthesis,
    CloseParenthesis,
    Power,
    // B
    Multiplication,
    Division,
    Modulo,
    Remaining,
    // C
    Addition,
    Substraction,
    // D ?
    Greater,
    Lesser,
    EqGreater,
    EqLesser,
    And,
    Or,
}

#[derive(Debug)]
pub enum MathNode {
    Operation(Box<MathNode>, Operation, Box<MathNode>),
    Float(f64),
    Int(i64),
}

fn get_split(tokens: &Vec<Token>, sep: Vec<Operation>) -> Result<Option<MathNode>, ()> {
    let mut in_parenthesis = 0;
    // check if in parenthesis ! TODO
    for i in (0..tokens.len()).rev() {
        if let Token::Operation(op) = &tokens[i] {
            match op {
                // attention on va a l'envers !!
                Operation::CloseParenthesis => {
                    in_parenthesis += 1;
                }
                Operation::OpenParenthesis => {
                    in_parenthesis -= 1;
                }
                _ => {
                    if in_parenthesis != 0 {
                        continue;
                    }
                    if sep.iter().find(|&o| o == op) == None {
                        continue;
                    }
                    let left = parse_math_expression(tokens[..i].into())?;
                    todo!("{:?}", left);
                    let right = parse_math_expression(tokens[..i].into())?;
                    return Ok(Some(MathNode::Operation(
                        Box::new(left),
                        op.clone(),
                        Box::new(right),
                    )));
                }
            }
        }
    }
    Ok(None)
}

pub fn parse_math_expression(tokens: Vec<Token>) -> Result<MathNode, ()> {
    // && ||
    let split = get_split(&tokens, vec![Operation::And, Operation::Or])?;
    if let Some(r) = split {
        return Ok(r);
    }

    // > => < =<
    let split = get_split(
        &tokens,
        vec![
            Operation::EqLesser,
            Operation::EqGreater,
            Operation::Greater,
            Operation::Lesser,
        ],
    )?;
    if let Some(r) = split {
        return Ok(r);
    }

    // + -
    let split = get_split(&tokens, vec![Operation::Addition, Operation::Substraction])?;
    if let Some(r) = split {
        return Ok(r);
    }

    // * % / //
    let split = get_split(
        &tokens,
        vec![
            Operation::Multiplication,
            Operation::Modulo,
            Operation::Division,
            Operation::Remaining,
        ],
    )?;
    if let Some(r) = split {
        return Ok(r);
    }

    // ^
    let split = get_split(&tokens, vec![Operation::Power])?;
    if let Some(r) = split {
        return Ok(r);
    }

    //todo!("{:?}, {:?}, {:?}", before, middle, after);
    Err(())
}

#[cfg(test)]
mod math_tests {
    use super::*;
    #[test]
    fn parse2() {
        let _re = parse_math_expression(vec![
            Token::Int(1),
            Token::Operation(Operation::Addition),
            Token::Operation(Operation::OpenParenthesis),
            Token::Int(1),
            Token::Operation(Operation::Addition),
            Token::Int(1),
            Token::Operation(Operation::CloseParenthesis),
            Token::Operation(Operation::Addition),
            Token::Int(1),
        ]);
    }

    #[test]
    fn parse_no_p() {
        let _re = parse_math_expression(vec![
            Token::Int(1),
            Token::Operation(Operation::Addition),
            Token::Int(1),
        ]);
    }

    #[test]
    fn parse_bool() {
        let _re = parse_math_expression(vec![
            Token::Int(1),
            Token::Operation(Operation::And),
            Token::Int(1),
        ]);
    }

    #[test]
    fn parse() {
        let _re = parse_math_expression(vec![
            Token::Operation(Operation::OpenParenthesis),
            Token::Int(1),
            Token::Operation(Operation::Addition),
            Token::Int(1),
            Token::Operation(Operation::CloseParenthesis),
        ]);
    }
}
