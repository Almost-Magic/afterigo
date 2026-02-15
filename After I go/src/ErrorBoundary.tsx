import React from 'react';

class ErrorBoundary extends React.Component<{children: React.ReactNode}, {hasError: boolean, error: string}> {
  constructor(props: any) {
    super(props);
    this.state = { hasError: false, error: '' };
  }
  static getDerivedStateFromError(error: Error) {
    return { hasError: true, error: error.message };
  }
  render() {
    if (this.state.hasError) {
      return (
        <div style={{color:'red',padding:'40px',background:'#1a1a2e',minHeight:'100vh'}}>
          <h1>App Crashed</h1>
          <pre>{this.state.error}</pre>
        </div>
      );
    }
    return this.props.children;
  }
}
export default ErrorBoundary;
