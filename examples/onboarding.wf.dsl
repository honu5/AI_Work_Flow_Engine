workflow onboarding_from_dsl {
  node greet plugin echo {
    message: "welcome"
  }
  node normalize plugin text.normalize {
    text: "  New User  "
    lowercase: true
    strip: true
  } depends greet
}
