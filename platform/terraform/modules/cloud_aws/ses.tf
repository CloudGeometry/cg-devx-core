data "aws_route53_zone" "selected" {
  name         = var.domain_name
}

resource "aws_ses_domain_identity" "this" {
  domain = var.domain_name
}

resource "aws_ses_email_identity" "this" {
  email = var.alert_emails[0]
}

resource "aws_route53_record" "example_amazonses_verification_record" {
  zone_id = data.aws_route53_zone.selected.id
  name    = "_amazonses.${var.domain_name}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.this.verification_token]
}