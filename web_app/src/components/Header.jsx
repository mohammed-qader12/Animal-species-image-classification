export default function Header() {
  return (
    <header className="header">
      <div className="header-inner">
        <span className="logo-mark">🐾</span>
        <div>
          <div className="site-title">Animal Species Classifier</div>
          <div className="site-sub">وردەکاری زیندەوەرەکان بە هۆشی دەستکرد</div>
        </div>
      </div>
      <span className="badge">153 Species · ResNet18</span>
    </header>
  )
}
