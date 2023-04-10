use crate::math::tokenizer::Token;

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

#[derive(Debug, PartialEq, Clone)]
pub enum MathNode {
    Operation(Box<MathNode>, Operation, Box<MathNode>),
    Float(f64),
    Int(isize),
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
                    let right = parse_math_expression(tokens[i + 1..].into())?;
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

fn remove_parenthesis(tokens: Vec<Token>) -> Result<Vec<Token>, ()> {
    if tokens[0] != Token::Operation(Operation::OpenParenthesis) {
        return Ok(tokens);
    }
    if tokens[tokens.len() - 1] != Token::Operation(Operation::CloseParenthesis) {
        return Ok(tokens);
    }
    for token in tokens[1..tokens.len() - 1].iter() {
        if let Token::Operation(op) = token {
            match op {
                Operation::OpenParenthesis => {
                    return Ok(tokens);
                }
                Operation::CloseParenthesis => {
                    return Ok(tokens);
                }
                _ => {}
            }
        }
    }
    Ok(tokens[1..tokens.len() - 1].into())
}

pub fn parse_math_expression(tokens: Vec<Token>) -> Result<MathNode, ()> {
    if tokens.len() == 0 {
        return Err(());
    }
    let tokens = remove_parenthesis(tokens)?;

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

    if tokens.len() == 1 {
        if let Token::Int(i) = tokens[0] {
            return Ok(MathNode::Int(i));
        }
        if let Token::Float(f) = tokens[0] {
            return Ok(MathNode::Float(f));
        }
    }
    Err(())
}

#[cfg(test)]
mod math_tests {
    use super::*;
    /* TODO check
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
        assert_eq!(
            _re,
            Ok(MathNode::Operation(
                Box::new(MathNode::Int(1)),
                Operation::Addition,
                Box::new(MathNode::Operation(
                    Box::new(MathNode::Int(1)),
                    Operation::Addition,
                    Box::new(MathNode::Int(1))
                ))
            ))
        );
    }
    */

    #[test]
    fn parse_no_p() {
        let _re = parse_math_expression(vec![
            Token::Float(1.0),
            Token::Operation(Operation::Addition),
            Token::Int(1),
        ]);
        assert_eq!(
            _re,
            Ok(MathNode::Operation(
                Box::new(MathNode::Float(1.0)),
                Operation::Addition,
                Box::new(MathNode::Int(1))
            ))
        );
    }

    #[test]
    fn parse_bool() {
        let _re = parse_math_expression(vec![
            Token::Int(1),
            Token::Operation(Operation::And),
            Token::Int(1),
        ]);
        assert_eq!(
            _re,
            Ok(MathNode::Operation(
                Box::new(MathNode::Int(1)),
                Operation::And,
                Box::new(MathNode::Int(1))
            ))
        );
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
        assert_eq!(
            _re,
            Ok(MathNode::Operation(
                Box::new(MathNode::Int(1)),
                Operation::Addition,
                Box::new(MathNode::Int(1))
            ))
        );
    }
}
