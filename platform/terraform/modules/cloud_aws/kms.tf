resource "aws_kms_key" "secret_manager_unseal" {
  description             = "CGDevX secret manager unseal key"
  deletion_window_in_days = 7

}

resource "aws_kms_alias" "secret_manager_unseal" {
  target_key_id = aws_kms_key.secret_manager_unseal.key_id
}
