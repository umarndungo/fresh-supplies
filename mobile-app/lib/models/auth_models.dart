/// Mirrors backend/app/application/mobile_schemas.py::MobileUserOut.
class MobileUser {
  final String id;
  final String? email;
  final String? phoneNumber; // legacy accounts created before the email-OTP switch
  final String role;
  final String? fullName;
  final String? accountType;
  final String? cooperativeId;
  final bool profileCompleted;

  const MobileUser({
    required this.id,
    required this.email,
    required this.phoneNumber,
    required this.role,
    required this.fullName,
    required this.accountType,
    required this.cooperativeId,
    required this.profileCompleted,
  });

  factory MobileUser.fromJson(Map<String, dynamic> json) => MobileUser(
        id: json['id'] as String,
        email: json['email'] as String?,
        phoneNumber: json['phoneNumber'] as String?,
        role: json['role'] as String,
        fullName: json['fullName'] as String?,
        accountType: json['accountType'] as String?,
        cooperativeId: json['cooperativeId'] as String?,
        profileCompleted: json['profileCompleted'] as bool? ?? false,
      );
}

/// Mirrors MobileAuthTokensOut — the response of otp/verify, refresh.
class AuthTokens {
  final String accessToken;
  final int expiresIn;
  final String refreshToken;
  final MobileUser user;

  const AuthTokens({required this.accessToken, required this.expiresIn, required this.refreshToken, required this.user});

  factory AuthTokens.fromJson(Map<String, dynamic> json) => AuthTokens(
        accessToken: json['accessToken'] as String,
        expiresIn: json['expiresIn'] as int,
        refreshToken: json['refreshToken'] as String,
        user: MobileUser.fromJson(json['user'] as Map<String, dynamic>),
      );
}
