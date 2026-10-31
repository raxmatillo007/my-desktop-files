const jwt = require('jsonwebtoken');

function authenticateToken(req, res, next) {
  const auth = req.headers['authorization'];
  const token = auth && auth.split(' ')[1];
  if (!token) return res.status(401).json({ error: 'Token kerak' });
  try {
    req.user = jwt.verify(token, process.env.JWT_SECRET || 'caretrack_jwt_2026');
    next();
  } catch {
    res.status(401).json({ error: "Token noto'g'ri" });
  }
}

function authorizeRole(...roles) {
  return (req, res, next) => {
    if (!roles.includes(req.user?.role)) {
      return res.status(403).json({ error: 'Kirish taqiqlandi' });
    }
    next();
  };
}

module.exports = { authenticateToken, authorizeRole };
