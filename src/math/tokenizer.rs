use crate::math::math_parser::Operation;

#[derive(Debug, PartialEq)]
pub enum TokenError {
    Uncomplete,
    Other(String),
}

#[derive(Debug, PartialEq, Clone)]
pub enum Token {
    Int(isize),
    Float(f64),
    Operation(Operation),
}

pub fn tokenize_expression(expression: &str) -> Result<Vec<Token>, TokenError> {
    let expression = expression.to_string() + " ";
    let mut chars = expression.chars().peekable();
    let mut tokens: Vec<Token> = Vec::new();

    while let Some(c) = chars.next() {
        if c.is_ascii_digit() {
            let mut token = String::new();
            let mut is_float = false;
            token.push(c);
            if let Some(c) = chars.peek() {
                if c == &'.' {
                    is_float = true;
                    token.push(chars.next().unwrap());
                } else if !c.is_ascii_digit() {
                    tokens.push(Token::Int(token.parse().unwrap()));
                    continue;
                }
            }
            while let Some(c) = chars.next() {
                if c == '.' {
                    if is_float {
                        return Err(TokenError::Other("to much points".to_string()));
                    }
                    is_float = true;
                }
                if c.is_ascii_digit() || c == '.' {
                    token.push(c);
                } else {
                    if is_float {
                        tokens.push(Token::Float(token.parse().unwrap()));
                    } else {
                        tokens.push(Token::Int(token.parse().unwrap()));
                    }
                    break;
                }
            }
        } else {
            match c {
                ' ' => {}
                '^' => tokens.push(Token::Operation(Operation::Power)),
                '+' => tokens.push(Token::Operation(Operation::Addition)),
                '-' => tokens.push(Token::Operation(Operation::Substraction)),
                '*' => tokens.push(Token::Operation(Operation::Multiplication)),
                '%' => tokens.push(Token::Operation(Operation::Modulo)),
                '(' => tokens.push(Token::Operation(Operation::OpenParenthesis)),
                ')' => tokens.push(Token::Operation(Operation::CloseParenthesis)),
                '/' => {
                    if let Some(c) = chars.peek() {
                        if *c == '/' {
                            tokens.push(Token::Operation(Operation::Remaining));
                            chars.next();
                        } else {
                            tokens.push(Token::Operation(Operation::Division));
                        }
                    } else {
                        return Err(TokenError::Uncomplete);
                    }
                }
                '>' => {
                    if let Some(c) = chars.peek() {
                        if *c == '=' {
                            tokens.push(Token::Operation(Operation::EqGreater));
                            chars.next();
                        } else {
                            tokens.push(Token::Operation(Operation::Greater));
                        }
                    } else {
                        return Err(TokenError::Uncomplete);
                    }
                }
                '<' => {
                    if let Some(c) = chars.peek() {
                        if *c == '=' {
                            tokens.push(Token::Operation(Operation::EqLesser));
                            chars.next();
                        } else {
                            tokens.push(Token::Operation(Operation::Lesser));
                        }
                    } else {
                        return Err(TokenError::Uncomplete);
                    }
                }
                '&' => {
                    if let Some(c) = chars.peek() {
                        if *c == '&' {
                            tokens.push(Token::Operation(Operation::And));
                            chars.next();
                        } else {
                            return Err(TokenError::Uncomplete);
                        }
                    } else {
                        return Err(TokenError::Uncomplete);
                    }
                }
                '|' => {
                    if let Some(c) = chars.peek() {
                        if *c == '|' {
                            tokens.push(Token::Operation(Operation::Or));
                            chars.next();
                        } else {
                            return Err(TokenError::Uncomplete);
                        }
                    } else {
                        return Err(TokenError::Uncomplete);
                    }
                }
                _ => {
                    return Err(TokenError::Other(
                        "pas reconu: ".to_string() + &c.to_string(),
                    ))
                }
            } // match
        }
    } // while
    Ok(tokens)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn simple_addition() {
        assert_eq!(
            tokenize_expression("1 + 1"),
            Ok(vec![
                Token::Int(1),
                Token::Operation(Operation::Addition),
                Token::Int(1)
            ])
        );
    }

    #[test]
    fn stick_simple_addition() {
        assert_eq!(
            tokenize_expression("1+1"),
            Ok(vec![
                Token::Int(1),
                Token::Operation(Operation::Addition),
                Token::Int(1)
            ])
        );
    }

    #[test]
    fn basic_float_working() {
        assert_eq!(
            tokenize_expression("1 + 1.1"),
            Ok(vec![
                Token::Int(1),
                Token::Operation(Operation::Addition),
                Token::Float(1.1)
            ])
        );
    }
}
